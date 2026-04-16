"""
AICS - 公募基金客户服务部AI辅助系统
Flask应用工厂模块
"""

import os
import logging
from datetime import datetime
from flask import Flask, request
from flask_cors import CORS

from app.config import config_by_name


def create_app(config_name=None):
    """
    Flask应用工厂函数
    
    Args:
        config_name: 配置环境名称 (development/testing/production)
    
    Returns:
        Flask应用实例
    """
    # 从环境变量获取配置，默认为development
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    config = config_by_name.get(config_name)
    if config is None:
        config = config_by_name['development']
    app.config.from_object(config)
    
    # 确保数据目录存在
    os.makedirs(app.config.get('DATA_DIR', './data'), exist_ok=True)
    
    # 配置日志
    _configure_logging(app)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"]
        }
    })
    
    # 注册请求钩子 - 添加trace_id
    @app.before_request
    def add_trace_id():
        """为每个请求生成或继承trace_id"""
        trace_id = request.headers.get('X-Request-ID') or request.headers.get('X-Trace-ID')
        if not trace_id:
            import uuid
            trace_id = f"tr_{uuid.uuid4().hex[:16]}"
        request.trace_id = trace_id
    
    # 注册蓝图
    _register_blueprints(app)
    
    # 注册错误处理器
    from app.utils.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # 记录启动信息
    app.logger.info(f"AICS Backend started - Environment: {config_name}")
    app.logger.info(f"Data directory: {app.config.get('DATA_DIR')}")
    
    return app


def _configure_logging(app):
    """配置日志系统"""
    log_level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    
    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    )
    
    # 配置根日志记录器
    app.logger.setLevel(log_level)
    
    # 移除默认处理器
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # 如果是生产环境，添加文件处理器
    if not app.config.get('DEBUG') and not app.config.get('TESTING'):
        log_dir = os.path.join(os.path.dirname(app.root_path), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'aics_{datetime.now().strftime("%Y%m%d")}.log')
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


def _register_blueprints(app):
    """注册所有蓝图"""
    # 系统相关路由
    from app.routes.health import health_bp
    app.register_blueprint(health_bp, url_prefix='/api/v1/system')
    
    # F1 客服模块 - 认证授权
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    # F1 客服模块 - 知识库管理
    from app.routes.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp, url_prefix='/api/v1/cs/knowledge')
    
    # F1 客服模块 - 智能问答
    from app.routes.qa import qa_bp
    app.register_blueprint(qa_bp, url_prefix='/api/v1/cs/qa')
    
    # TODO: 后续添加其他业务模块蓝图
    # from app.routes.cs import cs_bp
    # app.register_blueprint(cs_bp, url_prefix='/api/v1/cs')
    
    # F1 客服模块 - 投诉管理
    from app.routes.complaint import complaint_bp
    app.register_blueprint(complaint_bp, url_prefix='/api/v1/cs/complaints')
    
    # F1 客服模块 - 话术生成
    from app.routes.script import script_bp
    app.register_blueprint(script_bp, url_prefix='/api/v1/cs/scripts')
    
    # F1 客服模块 - 质检管理
    from app.routes.quality import quality_bp
    app.register_blueprint(quality_bp, url_prefix='/api/v1/cs/quality')
    
    # F1 客服模块 - 培训管理
    from app.routes.training import training_bp
    app.register_blueprint(training_bp, url_prefix='/api/v1/cs/training')
    
    # F2 高净值客户服务模块
    from app.routes.hnw import hnw_bp
    app.register_blueprint(hnw_bp, url_prefix='/api/v1/hnw')
    
    # F3 数据分析与洞察模块
    from app.routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    
    # F4 投教与合规模块
    from app.routes.education import education_bp
    app.register_blueprint(education_bp, url_prefix='/api/v1/education')
    
    from app.routes.compliance import compliance_bp
    app.register_blueprint(compliance_bp, url_prefix='/api/v1/compliance')
    
    # F5 市场监测与产品研究模块
    from app.routes.market import market_bp
    app.register_blueprint(market_bp, url_prefix='/api/v1/market')


# 应用启动时间（用于计算运行时间）
app_start_time = datetime.utcnow()
