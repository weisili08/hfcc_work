# AICS - 公募基金客服AI辅助系统

> AI-powered Customer Service System for Fund Management Companies

## 项目简介

AICS（AI Customer Service）是专为公募基金客户服务部设计的智能辅助系统，旨在通过AI技术提升客服效率、优化客户体验、加强合规管理。系统涵盖智能问答、知识库管理、高净值客户服务、数据分析、投资者教育、市场监测等核心功能模块。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                      │
│                    React 18 + Vite 5                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ F1客服   │ │ F2高净值│ │ F3数据  │ │ F4投教  │ │ F5市场  ││
│  │ 服务模块 │ │ 客户模块│ │ 分析模块│ │ 合规模块│ │ 监测模块││
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────┐
│                        后端层 (Backend)                       │
│                    Python 3.11 + Flask 3                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  API路由层  │  业务服务层  │  数据存储层  │  LLM服务层   ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 架构特点

- **前后端分离**：前端React SPA，后端Flask REST API
- **模块化设计**：5大业务模块独立开发、独立部署
- **JSON文件存储**：轻量级数据持久化，适合中小型应用
- **LLM集成**：支持OpenAI等主流大模型API

## 功能模块

### F1 客户服务管理模块

| 功能 | 描述 | API端点 |
|------|------|---------|
| 智能问答 | AI驱动的客户问题自动回答 | `POST /api/v1/cs/qa/ask` |
| 知识库管理 | 知识文档的CRUD操作 | `/api/v1/cs/knowledge/*` |
| 投诉管理 | 客户投诉记录与处理跟踪 | `/api/v1/cs/complaints/*` |
| 话术生成 | AI生成标准客服话术 | `/api/v1/cs/scripts/*` |
| 质检管理 | 服务质量检查与评分 | `/api/v1/cs/quality/*` |
| 培训管理 | 员工培训计划与考核 | `/api/v1/cs/training/*` |

### F2 高净值客户服务模块

| 功能 | 描述 | API端点 |
|------|------|---------|
| 客户管理 | 高净值客户档案管理 | `/api/v1/hnw/customers/*` |
| 资产配置建议 | AI生成个性化配置方案 | `/api/v1/hnw/allocation/*` |
| 客户关怀 | 生日提醒、节日问候等 | `/api/v1/hnw/care/*` |
| 活动管理 | 专属客户活动组织 | `/api/v1/hnw/events/*` |

### F3 数据分析与洞察模块

| 功能 | 描述 | API端点 |
|------|------|---------|
| 客户画像 | 多维度客户特征分析 | `/api/v1/analytics/profiles/*` |
| 异常监控 | 交易异常行为检测 | `/api/v1/analytics/anomalies/*` |
| 流失预警 | 客户流失风险预测 | `/api/v1/analytics/churn/*` |
| 报表中心 | 多维度数据报表生成 | `/api/v1/analytics/reports/*` |

### F4 投资者教育与合规模块

| 功能 | 描述 | API端点 |
|------|------|---------|
| 投教内容 | 投资者教育材料管理 | `/api/v1/education/*` |
| 合规检查 | 业务合规性自动检查 | `/api/v1/compliance/checks/*` |
| 风险提示 | 投资风险预警提示 | `/api/v1/compliance/risk-alerts/*` |

### F5 市场监测与产品研究模块

| 功能 | 描述 | API端点 |
|------|------|---------|
| 舆情监控 | 市场舆情实时监测 | `/api/v1/market/sentiment/*` |
| 产品研究 | 基金产品分析报告 | `/api/v1/market/products/*` |
| 市场动态 | 市场行情与资讯 | `/api/v1/market/dynamics/*` |

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| Flask | 3.0+ | Web框架 |
| Flask-CORS | 4.0+ | 跨域支持 |
| PyJWT | 2.8+ | JWT认证 |
| Gunicorn | 21.2+ | WSGI服务器 |
| python-dotenv | 1.0+ | 环境变量管理 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2+ | UI框架 |
| Vite | 5.0+ | 构建工具 |
| React Router | 6.20+ | 路由管理 |
| Axios | 1.6+ | HTTP客户端 |

### 部署

| 技术 | 用途 |
|------|------|
| Docker | 容器化 |
| Docker Compose | 多服务编排 |
| Nginx | 反向代理、静态文件服务 |

## 快速启动

### 方式一：Docker部署（推荐）

```bash
# 1. 克隆项目
cd /Users/liuchang/openclaw/hfcc_work/aics

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入必要的配置

# 3. 启动服务
docker-compose up --build

# 4. 访问系统
# 前端: http://localhost
# 后端API: http://localhost:5000
```

### 方式二：手动启动

**后端启动：**

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
python run.py
# 或使用 gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

**前端启动：**

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 构建生产版本
npm run build
```

### 方式三：一键启动脚本

```bash
# 赋予执行权限
chmod +x start.sh

# 执行启动脚本
./start.sh
```

## 环境变量配置

复制 `backend/.env.example` 为 `backend/.env` 并配置以下变量：

```bash
# Flask配置
FLASK_ENV=development          # 环境: development/testing/production
SECRET_KEY=your-secret-key     # 密钥（生产环境必须修改）

# LLM API配置
LLM_API_KEY=your-api-key       # OpenAI或其他LLM API密钥
LLM_API_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
LLM_TIMEOUT=30

# 备用LLM配置（可选）
LLM_BACKUP_API_KEY=
LLM_BACKUP_API_URL=
LLM_BACKUP_MODEL=

# 数据目录
DATA_DIR=./data
```

## API文档

### 系统健康检查

```
GET /api/v1/system/health
GET /api/v1/system/capabilities
```

### 认证相关

```
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/profile
```

### 主要业务端点

| 模块 | 基础路径 | 描述 |
|------|----------|------|
| 知识库 | `/api/v1/cs/knowledge` | 知识文档管理 |
| 智能问答 | `/api/v1/cs/qa` | AI问答服务 |
| 投诉管理 | `/api/v1/cs/complaints` | 投诉记录管理 |
| 话术生成 | `/api/v1/cs/scripts` | 客服话术生成 |
| 质检管理 | `/api/v1/cs/quality` | 服务质量检查 |
| 培训管理 | `/api/v1/cs/training` | 培训计划管理 |
| 高净值客户 | `/api/v1/hnw` | HNW客户服务 |
| 数据分析 | `/api/v1/analytics` | 数据洞察分析 |
| 投资者教育 | `/api/v1/education` | 投教内容管理 |
| 合规管理 | `/api/v1/compliance` | 合规检查管理 |
| 市场监测 | `/api/v1/market` | 市场舆情监测 |

## 项目目录结构

```
aics/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py        # Flask应用工厂
│   │   ├── config.py          # 配置管理
│   │   ├── models/            # 数据模型
│   │   ├── routes/            # API路由
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── knowledge.py   # 知识库
│   │   │   ├── qa.py          # 智能问答
│   │   │   ├── complaint.py   # 投诉管理
│   │   │   ├── script.py      # 话术生成
│   │   │   ├── quality.py     # 质检管理
│   │   │   ├── training.py    # 培训管理
│   │   │   ├── hnw.py         # 高净值客户
│   │   │   ├── analytics.py   # 数据分析
│   │   │   ├── education.py   # 投资者教育
│   │   │   ├── compliance.py  # 合规管理
│   │   │   └── market.py      # 市场监测
│   │   ├── services/          # 业务服务层
│   │   ├── storage/           # 数据存储层
│   │   └── utils/             # 工具函数
│   ├── data/                  # JSON数据文件
│   ├── tests/                 # 测试用例
│   ├── Dockerfile             # 后端Dockerfile
│   ├── requirements.txt       # Python依赖
│   ├── run.py                 # 启动入口
│   └── .env.example           # 环境变量示例
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── pages/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   ├── services/          # API服务
│   │   ├── stores/            # 状态管理
│   │   └── utils/             # 工具函数
│   ├── dist/                  # 构建产物
│   ├── Dockerfile             # 前端Dockerfile
│   ├── nginx.conf             # Nginx配置
│   ├── package.json           # Node依赖
│   └── vite.config.js         # Vite配置
├── docker-compose.yml         # Docker编排配置
├── start.sh                   # 一键启动脚本
└── README.md                  # 项目说明
```

## 开发说明

### 代码规范

- 后端遵循 PEP 8 规范
- 前端使用 ESLint 进行代码检查
- 提交前请运行测试：`pytest`（后端）

### 添加新功能

1. 在 `app/routes/` 创建新的路由文件
2. 在 `app/services/` 实现业务逻辑
3. 在 `app/storage/` 添加数据存储（如需要）
4. 更新 `app/__init__.py` 注册蓝图
5. 编写测试用例

### 测试

```bash
# 后端测试
cd backend
pytest

# 覆盖率测试
pytest --cov=app tests/
```

## 许可证

本项目为内部使用，未经授权不得对外发布。

## 联系方式

如有问题或建议，请联系项目维护团队。

---

**版本**: 1.0.0  
**最后更新**: 2026年4月
