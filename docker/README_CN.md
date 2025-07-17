## Docker 部署说明文档

欢迎使用新的 `docker` 目录来通过 Docker Compose 部署 Dify。本文档概述了更新内容、部署说明以及现有用户的迁移详情。

### 更新内容

- **Certbot 容器**：`docker-compose.yaml` 现在包含 `certbot` 用于管理 SSL 证书。该容器会自动续期证书并确保安全的 HTTPS 连接。
  更多信息请参考 `docker/certbot/README.md`。

- **持久化环境变量**：环境变量现在通过 `.env` 文件进行管理，确保您的配置在部署过程中保持持久化。

  > 什么是 `.env` 文件？</br> </br>
  > `.env` 文件是 Docker 和 Docker Compose 环境中的关键组件，作为集中配置文件，您可以在其中定义容器运行时可访问的环境变量。该文件简化了开发、测试和生产不同阶段的环境设置管理，为部署提供一致性和配置便利性。

- **统一的向量数据库服务**：所有向量数据库服务现在都通过单个 Docker Compose 文件 `docker-compose.yaml` 进行管理。您可以通过在 `.env` 文件中设置 `VECTOR_STORE` 环境变量来切换不同的向量数据库。
- **必需的 .env 文件**：现在运行 `docker compose up` 需要 `.env` 文件。该文件对于配置您的部署以及任何自定义设置通过升级保持持久化至关重要。

### 如何使用 `docker-compose.yaml` 部署 Dify

1. **前置条件**：确保您的系统已安装 Docker 和 Docker Compose。
2. **环境设置**：
    - 导航到 `docker` 目录。
    - 通过运行 `cp .env.example .env` 将 `.env.example` 文件复制到名为 `.env` 的新文件。
    - 根据需要自定义 `.env` 文件。请参考 `.env.example` 文件了解详细的配置选项。
3. **运行服务**：
    - 从 `docker` 目录执行 `docker compose up` 来启动服务。
    - 要指定向量数据库，请在 `.env` 文件中将 `VECTOR_STORE` 变量设置为您所需的向量数据库服务，如 `milvus`、`weaviate` 或 `opensearch`。
4. **SSL 证书设置**：
    - 参考 `docker/certbot/README.md` 使用 Certbot 设置 SSL 证书。
5. **OpenTelemetry Collector 设置**：
    - 在 `.env` 中将 `ENABLE_OTEL` 更改为 `true`。
    - 正确配置 `OTLP_BASE_ENDPOINT`。

### 如何部署开发 Dify 所需的中间件
1. **中间件设置**：
    - 使用 `docker-compose.middleware.yaml` 设置必要的中间件服务，如数据库和缓存。
    - 导航到 `docker` 目录。
    - 通过运行 `cp middleware.env.example middleware.env` 确保创建 `middleware.env` 文件（参考 `middleware.env.example` 文件）。
2. **运行中间件服务**：
    - 导航到 `docker` 目录。
    - 执行 `docker compose -f docker-compose.middleware.yaml --profile weaviate -p dify up -d` 来启动中间件服务。（如果您不使用 weaviate，请将配置文件更改为其他向量数据库）

### 现有用户的迁移

对于从 `docker-legacy` 设置迁移的用户：

1. **审查更改**：熟悉新的 `.env` 配置和 Docker Compose 设置。
2. **转移自定义配置**：
    - 如果您有自定义配置，如 `docker-compose.yaml`、`ssrf_proxy/squid.conf` 或 `nginx/conf.d/default.conf`，您需要在创建的 `.env` 文件中反映这些更改。
3. **数据迁移**：
    - 确保来自数据库和缓存等服务的数据得到适当备份，并在必要时迁移到新结构。

### `.env` 文件概述

#### 关键模块和自定义配置

- **向量数据库服务**：根据使用的向量数据库类型（`VECTOR_STORE`），用户可以设置特定的端点、端口和身份验证详细信息。
- **存储服务**：根据存储类型（`STORAGE_TYPE`），用户可以配置 S3、Azure Blob、Google Storage 等的特定设置。
- **API 和 Web 服务**：用户可以定义影响 API 和 Web 前端运行的 URL 和其他设置。

#### 其他重要变量

`.env.example` 文件非常全面，涵盖了广泛的配置选项。它分为几个部分，每个部分涉及应用程序及其服务的不同方面。以下是一些关键部分和变量：

1. **通用变量**：
    - `CONSOLE_API_URL`、`SERVICE_API_URL`：不同 API 服务的 URL。
    - `APP_WEB_URL`：前端应用程序 URL。
    - `FILES_URL`：文件下载和预览的基础 URL。
2. **服务器配置**：
    - `LOG_LEVEL`、`DEBUG`、`FLASK_DEBUG`：日志记录和调试设置。
    - `SECRET_KEY`：用于加密会话 cookie 和其他敏感数据的密钥。
3. **数据库配置**：
    - `DB_USERNAME`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`、`DB_DATABASE`：PostgreSQL 数据库凭据和连接详细信息。
4. **Redis 配置**：
    - `REDIS_HOST`、`REDIS_PORT`、`REDIS_PASSWORD`：Redis 服务器连接设置。
5. **Celery 配置**：
    - `CELERY_BROKER_URL`：Celery 消息代理的配置。
6. **存储配置**：
    - `STORAGE_TYPE`、`S3_BUCKET_NAME`、`AZURE_BLOB_ACCOUNT_NAME`：本地、S3、Azure Blob 等文件存储选项的设置。
7. **向量数据库配置**：
    - `VECTOR_STORE`：向量数据库类型（如 `weaviate`、`milvus`）。
    - 每个向量存储的特定设置，如 `WEAVIATE_ENDPOINT`、`MILVUS_URI`。
8. **CORS 配置**：
    - `WEB_API_CORS_ALLOW_ORIGINS`、`CONSOLE_CORS_ALLOW_ORIGINS`：跨域资源共享的设置。
9. **OpenTelemetry 配置**：
    - `ENABLE_OTEL`：在 api 中启用 OpenTelemetry collector。
    - `OTLP_BASE_ENDPOINT`：您的 OTLP 导出器的端点。
10. **其他服务特定的环境变量**：
    - 每个服务如 `nginx`、`redis`、`db` 和向量数据库都有在 `docker-compose.yaml` 中直接引用的特定环境变量。

### 附加信息

- **持续改进阶段**：我们正在积极寻求社区的反馈来完善和增强部署过程。随着更多用户采用这种新方法，我们将根据您的经验和建议继续改进。
- **支持**：有关详细配置选项和环境变量设置，请参考 `docker` 目录中的 `.env.example` 文件和 Docker Compose 配置文件。

本文档旨在指导您使用新的 Docker Compose 设置完成部署过程。如有任何问题或需要进一步帮助，请参考官方文档或联系支持团队。 