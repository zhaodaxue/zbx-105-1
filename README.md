# 🌾 丰收节临时摊位用电申报系统

乡镇丰收节筹备组 **临时摊位用电申报** 0-1 前后端分离小系统。

## ✨ 功能概览

| 角色 | 功能 |
|------|------|
| 🧑‍🌾 摊主 | 提交用电申报（摊位编号/区域、预估峰值千瓦、用电时段起止、是否明火厨灶） |
| ⚡ 电工 | 审核申报 → 批准（分配临时电表编号）/ 驳回（必填原因） |
| 📊 筹备员 | 查看当日各区域已批千瓦合计，导出 **CSV 摘要**（含各区域合计 + 明细） |

## 🏗️ 技术栈

- **后端**: FastAPI + SQLAlchemy + PostgreSQL + JWT
- **前端**: Vue 3 + Vite + Element Plus + Pinia + Vue Router
- **部署**: Docker Compose（一键启动 + PostgreSQL 持久化卷）

## 🚀 一条命令启动（推荐）

```bash
# 1. 复制环境变量（可选，默认即可运行）
cp .env.example .env    # Windows: copy .env.example .env

# 2. 构建并启动所有服务（首次构建约 3-5 分钟）
docker compose up -d --build
```

启动完成后访问：

| 服务 | 地址 |
|------|------|
| 🌐 前端页面 | http://localhost:8080 |
| 📖 后端 Swagger API 文档 | http://localhost:8000/docs |
| 🔌 PostgreSQL | localhost:5432 (库: harvest_db, 用户: postgres, 密码: postgres) |

> 💡 停止服务：`docker compose down`（数据仍保留在持久化卷 `harvest_postgres_data` 中）  
> 💡 彻底清除数据（含数据库）：`docker compose down -v`

## 👥 预置演示账号（首次启动自动创建）

| 账号 | 密码 | 角色 |
|------|------|------|
| `vendor1` | `vendor123` | 摊主（张摊主） |
| `vendor2` | `vendor123` | 摊主（李摊主） |
| `electrician1` | `elec123` | 电工（王电工） |
| `planner1` | `plan123` | 筹备员（赵筹备） |

## 📦 项目结构

```
zbx-105-1/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 入口 & 路由注册
│   │   ├── models.py       # SQLAlchemy 数据模型
│   │   ├── schemas.py      # Pydantic 请求/响应模型
│   │   ├── auth.py         # JWT 认证 & 角色权限
│   │   ├── database.py     # DB 连接 & 初始化
│   │   ├── config.py       # 配置加载
│   │   └── routers/        # API 路由
│   │       ├── auth.py
│   │       ├── applications.py
│   │       └── stats.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── views/          # 页面组件（登录/工作台/申报/审核/统计...）
│   │   ├── router/         # Vue Router（含路由守卫）
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── api/            # Axios 封装
│   │   └── utils/
│   ├── nginx.conf          # Nginx 反代配置
│   ├── Dockerfile          # 多阶段构建
│   └── package.json
├── docker-compose.yml       # 编排入口
├── .env.example             # 环境变量模板
└── README.md
```

## 🔌 主要 API 端点

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 登录获取 Token | 公开 |
| GET  | `/api/auth/me` | 获取当前用户信息 | 登录 |
| POST | `/api/applications` | 提交用电申报 | 摊主 |
| GET  | `/api/applications` | 查询申报列表 | 登录（摊主仅看自己） |
| GET  | `/api/applications/{id}` | 申报详情 | 登录 |
| PUT  | `/api/applications/{id}/review` | 审核（批准/驳回） | 电工 |
| GET  | `/api/stats/daily` | 当日各区域千瓦合计 | 筹备员/电工 |
| GET  | `/api/stats/export-csv` | 导出 CSV 摘要 | 筹备员/电工 |

## 🔧 本地开发（不使用 Docker）

### 后端

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate    # Windows
# source .venv/bin/activate                        # Linux/Mac
pip install -r requirements.txt
# 需要本地 PostgreSQL，修改 DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```
