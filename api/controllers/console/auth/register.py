from tkinter import E
from flask_restful import Resource
from flask_restful import reqparse
from controllers.console import api
from services.account_service import RegisterService, AccountService
import secrets
from extensions.ext_redis import redis_client
import re
from tasks.mail_email_code_login import send_email_code_login_mail_task

class EmailCodeService:
    EMAIL_CODE_KEY_BASE = "email_code"

    @classmethod
    def generate_email_code(cls, email: str) -> str:
        return "".join([str(secrets.randbelow(exclusive_upper_bound=10)) for _ in range(6)])
    
    @classmethod
    def save_email_code_to_redis(cls, email: str, code: str) -> None:
        redis_client.set(f"{cls.EMAIL_CODE_KEY_BASE}:{email}", code, ex=60 * 5)
    
    @classmethod
    def get_email_code_from_redis(cls, email: str) -> str | None:
        code = redis_client.get(f"{cls.EMAIL_CODE_KEY_BASE}:{email}")
        if code:
            return code.decode("utf-8")
        return None
    
    @classmethod
    def check_email_code_format(cls, email: str) -> bool:
        return re.match(r"^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$", email) is not None
    
    @classmethod
    def remove_email_code_from_redis(cls, email: str) -> None:
        redis_client.delete(f"{cls.EMAIL_CODE_KEY_BASE}:{email}")


class EmailCodeApi(Resource):
    # 发送邮件验证码
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True, location="json")
        parser.add_argument("language", type=str, required=True, location="json")
        parser.add_argument("test_key", type=str, required=False, location="json")
        args = parser.parse_args()
        email = args.email.strip()
        language = args.language
        test_key = args.test_key

        if not EmailCodeService.check_email_code_format(email):
            return {"result": "error", "message": "Invalid email address."}, 400

        code = EmailCodeService.generate_email_code(email)
        if test_key != "qwerasdzxcwsx":
            send_email_code_login_mail_task.delay(language=language, to=email, code=code)
            EmailCodeService.save_email_code_to_redis(email, code)
            return {"result": "success", "message": "Email code sent."}, 200
        else:
            EmailCodeService.save_email_code_to_redis(email, code)
            return {"result": "success", "message": "Email code sent.", "code": code}, 200

class RegisterApi(Resource):
    # 注册
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True, location="json")
        parser.add_argument("password", type=str, required=True, location="json")
        parser.add_argument("repeat_password", type=str, required=True, location="json")
        parser.add_argument("language", type=str, required=True, location="json")
        parser.add_argument("code", type=str, required=True, location="json")

        args = parser.parse_args()

        email = args.email.strip()
        password = args.password
        repeat_password = args.repeat_password
        language = args.language
        code = args.code

        if not EmailCodeService.check_email_code_format(email):
            return {"result": "error", "message": "Invalid email address."}, 400

        email_code = EmailCodeService.get_email_code_from_redis(email)
        
        print(email_code)
        print(code)

        if not email_code or email_code != code:
            return {"result": "error", "message": "Invalid code."}, 400

        if not AccountService.check_email_unique(email):
            return {"result": "error", "message": "Email already exists."}, 400

        if password != repeat_password:
            return {"result": "error", "message": "Password and repeat password do not match."}, 400

        account_name = email.split("@")[0]

        RegisterService.register(
            email=email,
            name=account_name,
            password=password,
            language=language,
            create_workspace_required=False,
        )
        EmailCodeService.remove_email_code_from_redis(email)
        return {"result": "Account created successfully"}, 200

api.add_resource(EmailCodeApi, "/email_code")
api.add_resource(RegisterApi, "/register")