"""
Pytest配置和共享fixtures
"""

import os
import sys
import pytest
import tempfile
import shutil

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.utils.auth import generate_token


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 测试结束后清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def app(temp_data_dir):
    """创建测试应用实例"""
    app = create_app('testing')
    # 使用临时数据目录
    app.config['DATA_DIR'] = temp_data_dir
    # 确保目录存在（包括所有子目录）
    os.makedirs(temp_data_dir, exist_ok=True)
    # 确保测试期间目录始终存在
    with app.app_context():
        # 强制创建数据目录
        os.makedirs(app.config.get('DATA_DIR', temp_data_dir), exist_ok=True)
    yield app
    # 测试结束后确保清理
    if os.path.exists(temp_data_dir):
        shutil.rmtree(temp_data_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建CLI测试runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(app):
    """创建认证请求头（使用测试token）"""
    with app.app_context():
        token = generate_token(
            user_id='test_user_001',
            role='admin',
            username='testuser'
        )
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def auth_headers_cs(app):
    """创建客服角色认证请求头"""
    with app.app_context():
        token = generate_token(
            user_id='cs_user_001',
            role='cs_agent',
            username='csagent'
        )
    return {'Authorization': f'Bearer {token}'}


class TestDataHelper:
    """测试数据辅助类"""
    
    @staticmethod
    def create_test_user():
        """创建测试用户数据"""
        return {
            'username': 'testuser',
            'password': 'testpass123',
            'name': '测试用户',
            'role': 'admin',
            'email': 'test@example.com',
            'department': '客服部'
        }
    
    @staticmethod
    def create_test_knowledge_base():
        """创建测试知识库数据"""
        return {
            'name': '测试知识库',
            'description': '用于测试的知识库',
            'category': 'general'
        }
    
    @staticmethod
    def create_test_document():
        """创建测试文档数据"""
        return {
            'title': '测试文档',
            'content': '这是测试文档的内容',
            'category': 'general',
            'tags': ['测试', '文档'],
            'source': '测试来源',
            'status': 'published'
        }
    
    @staticmethod
    def create_test_complaint():
        """创建测试投诉数据"""
        return {
            'title': '测试投诉',
            'customer_name': '测试客户',
            'customer_phone': '13800138000',
            'type': 'product',
            'description': '这是一个测试投诉描述',
            'priority': 'high',
            'created_by': 'test_user'
        }
    
    @staticmethod
    def create_test_script_request():
        """创建测试话术生成请求"""
        return {
            'scenario': 'product_inquiry',
            'context': {'product_name': '测试基金'},
            'style': 'professional',
            'created_by': 'test_user'
        }
    
    @staticmethod
    def create_test_quality_check():
        """创建测试质检记录"""
        return {
            'agent_name': '测试客服',
            'call_date': '2026-04-15',
            'call_duration': 300,
            'call_content': '客户：我想了解一下基金产品。客服：您好，请问有什么可以帮您？'
        }
    
    @staticmethod
    def create_test_training():
        """创建测试培训数据"""
        return {
            'title': '测试培训课程',
            'type': 'course',
            'category': '产品知识',
            'description': '这是一个测试培训课程',
            'content': '培训内容...',
            'duration_minutes': 60,
            'status': 'published',
            'difficulty': 'intermediate'
        }
    
    @staticmethod
    def create_test_hnw_customer():
        """创建测试高净值客户数据"""
        return {
            'name': '测试高净值客户',
            'phone': '13900139000',
            'email': 'hnw@example.com',
            'risk_level': 'moderate',
            'aum': 5000000,
            'tier': 'platinum',
            'manager_id': 'manager_001'
        }
    
    @staticmethod
    def create_test_education_content():
        """创建测试投教内容数据"""
        return {
            'title': '测试投教文章',
            'category': 'fund_basics',
            'target_audience': 'beginner',
            'content': '这是投教内容正文...',
            'format': 'article',
            'tags': ['基金', '入门'],
            'status': 'published'
        }


@pytest.fixture
def test_data():
    """提供测试数据辅助类"""
    return TestDataHelper()
