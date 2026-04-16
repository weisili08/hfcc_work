"""
AICS - 公募基金客户服务部AI辅助系统
Flask应用启动入口

使用方法:
    python run.py
    
或:
    flask --app run:app run
"""

import os
import sys

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 加载环境变量（如果存在.env文件）
try:
    from dotenv import load_dotenv
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
except ImportError:
    print("python-dotenv not installed, skipping .env loading")

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 获取配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = app.config.get('DEBUG', True)
    
    print(f"=" * 60)
    print(f"AICS Backend Server")
    print(f"=" * 60)
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug mode: {debug}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"API Base URL: http://{host}:{port}/api/v1")
    print(f"=" * 60)
    print(f"Health Check: http://{host}:{port}/api/v1/system/health")
    print(f"Capabilities: http://{host}:{port}/api/v1/system/capabilities")
    print(f"=" * 60)
    
    # 启动Flask开发服务器
    # 注意：生产环境应使用Gunicorn等WSGI服务器
    app.run(host=host, port=port, debug=debug)
