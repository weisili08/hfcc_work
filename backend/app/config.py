"""
AICS - 配置模块
支持多环境配置：开发、测试、生产
"""

import os


class Config:
    """
    基础配置类
    所有环境配置的基类
    """
    # Flask核心配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据目录配置
    DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'data'
    )
    
    # LLM API配置
    LLM_API_KEY = os.environ.get('LLM_API_KEY', 'sk-f47c2e9de62c4375800379e938e2c25b')
    LLM_API_URL = os.environ.get('LLM_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'qwen-plus')
    LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', '30'))
    
    # 备用LLM配置
    LLM_BACKUP_API_KEY = os.environ.get('LLM_BACKUP_API_KEY', '')
    LLM_BACKUP_API_URL = os.environ.get('LLM_BACKUP_API_URL', '')
    LLM_BACKUP_MODEL = os.environ.get('LLM_BACKUP_MODEL', '')
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # 分页默认配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 应用元信息
    APP_NAME = "合肥理财中心 - 公募基金客户关系部AI辅助系统"
    APP_VERSION = "1.0.0"
    
    @staticmethod
    def init_app(app):
        """初始化应用（可被子类重写）"""
        pass


class DevelopmentConfig(Config):
    """
    开发环境配置
    启用调试模式，详细日志输出
    """
    DEBUG = True
    TESTING = False
    
    # 开发环境使用更宽松的CORS设置
    CORS_ORIGINS = "*"
    
    # 开发环境日志级别
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """
    测试环境配置
    启用测试模式，使用独立测试数据目录
    """
    DEBUG = False
    TESTING = True
    
    # 测试环境使用独立的数据目录
    DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'test_data'
    )
    
    # 测试环境使用固定密钥
    SECRET_KEY = 'test-secret-key'
    
    # 测试环境日志级别
    LOG_LEVEL = "INFO"
    
    # 测试环境使用较短的超时
    LLM_TIMEOUT = 5


class ProductionConfig(Config):
    """
    生产环境配置
    关闭调试模式，严格的安全设置
    """
    DEBUG = False
    TESTING = False
    
    # 生产环境必须设置SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 生产环境CORS白名单（需要具体配置）
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')
    
    # 生产环境日志级别
    LOG_LEVEL = "WARNING"
    
    # 生产环境使用更严格的超时
    LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', '45'))


# 配置映射字典
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
