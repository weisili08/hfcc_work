# AICS 前端 Dockerfile
# 公募基金客服AI辅助系统 - React前端服务
# 多阶段构建：构建阶段 + 部署阶段

# ==================== Stage 1: 构建阶段 ====================
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# ==================== Stage 2: 部署阶段 ====================
FROM nginx:alpine

# 复制nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制dist文件到nginx目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露80端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
