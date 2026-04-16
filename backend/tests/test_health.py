"""
健康检查接口测试
"""

import pytest


class TestHealthEndpoints:
    """健康检查端点测试类"""
    
    def test_health_check_success(self, client):
        """测试健康检查接口返回成功"""
        response = client.get('/api/v1/system/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # 验证响应结构
        assert 'trace_id' in data
        assert 'data' in data
        assert 'meta' in data
        
        # 验证数据内容
        health_data = data['data']
        assert 'status' in health_data
        assert health_data['status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'version' in health_data
        assert 'timestamp' in health_data
        assert 'uptime_seconds' in health_data
        assert 'services' in health_data
        
        # 验证服务状态
        services = health_data['services']
        assert 'api' in services
        assert 'storage' in services
    
    def test_ping_endpoint(self, client):
        """测试ping接口"""
        response = client.get('/api/v1/system/ping')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['status'] == 'pong'
    
    def test_capabilities_endpoint(self, client):
        """测试能力探测接口"""
        response = client.get('/api/v1/system/capabilities')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        capabilities = data['data']
        
        # 验证响应结构
        assert 'api_version' in capabilities
        assert 'available_modules' in capabilities
        assert 'llm_capabilities' in capabilities
        assert 'storage_capabilities' in capabilities
        assert 'features' in capabilities
        
        # 验证模块列表
        modules = capabilities['available_modules']
        assert len(modules) >= 5  # 至少有5个业务模块
        
        # 验证每个模块的结构
        for module in modules:
            assert 'module_code' in module
            assert 'module_name' in module
            assert 'status' in module
            assert 'features' in module
            assert 'endpoints' in module
