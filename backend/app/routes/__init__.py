"""
路由模块
注册所有API蓝图
"""

# 导入所有蓝图
from app.routes.analytics import analytics_bp
from app.routes.auth import auth_bp
from app.routes.complaint import complaint_bp
from app.routes.compliance import compliance_bp
from app.routes.education import education_bp
from app.routes.health import health_bp
from app.routes.hnw import hnw_bp
from app.routes.knowledge import knowledge_bp
from app.routes.market import market_bp
from app.routes.qa import qa_bp
from app.routes.quality import quality_bp
from app.routes.script import script_bp
from app.routes.training import training_bp

__all__ = [
    'analytics_bp',
    'auth_bp',
    'complaint_bp',
    'compliance_bp',
    'education_bp',
    'health_bp',
    'hnw_bp',
    'knowledge_bp',
    'market_bp',
    'qa_bp',
    'quality_bp',
    'script_bp',
    'training_bp'
]
