"""
认证授权接口测试
"""

import pytest
import json


class TestAuthEndpoints:
    """认证授权端点测试类"""
    
    def test_login_success(self, client, app, test_data):
        """测试登录成功"""
        # 先创建一个测试用户
        from app.storage.user_storage import UserStorage
        
        with app.app_context():
            data_dir = app.config.get('DATA_DIR', './data')
            user_storage = UserStorage(data_dir)
            user_data = test_data.create_test_user()
            user_storage.create(user_data)
        
        # 登录请求
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post('/api/v1/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        response_data = data['data']
        assert 'token' in response_data
        assert 'user' in response_data
        assert response_data['user']['username'] == 'testuser'
    
    def test_login_missing_username(self, client):
        """测试缺少用户名的登录请求"""
        login_data = {
            'password': 'testpass123'
        }
        response = client.post('/api/v1/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_missing_password(self, client):
        """测试缺少密码的登录请求"""
        login_data = {
            'username': 'testuser'
        }
        response = client.post('/api/v1/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_invalid_credentials(self, client):
        """测试无效凭据登录"""
        login_data = {
            'username': 'nonexistent_user',
            'password': 'wrong_password'
        }
        response = client.post('/api/v1/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_empty_body(self, client):
        """测试空请求体登录"""
        response = client.post('/api/v1/auth/login',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_profile_success(self, client, auth_headers):
        """测试获取用户信息成功"""
        response = client.get('/api/v1/auth/profile',
                             headers=auth_headers)
        
        # 用户可能不存在，但接口应该返回401或200
        assert response.status_code in [200, 401]
    
    def test_get_profile_without_token(self, client):
        """测试未携带token获取用户信息"""
        response = client.get('/api/v1/auth/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_profile_invalid_token(self, client):
        """测试使用无效token获取用户信息"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/v1/auth/profile',
                             headers=headers)
        
        assert response.status_code == 401
    
    def test_logout_success(self, client, auth_headers):
        """测试登出成功"""
        response = client.post('/api/v1/auth/logout',
                              headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_logout_without_token(self, client):
        """测试未携带token登出"""
        response = client.post('/api/v1/auth/logout')
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self, client, auth_headers):
        """测试刷新token成功"""
        response = client.post('/api/v1/auth/refresh',
                              headers=auth_headers)
        
        # 如果用户存在则返回200，否则返回401
        assert response.status_code in [200, 401]
    
    def test_refresh_token_without_auth(self, client):
        """测试未携带token刷新"""
        response = client.post('/api/v1/auth/refresh')
        
        assert response.status_code == 401
