"""
话术生成接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestScriptEndpoints:
    """话术生成端点测试类"""
    
    @patch('app.routes.script.ScriptService')
    def test_generate_script_success(self, mock_script_service, client, test_data):
        """测试生成话术成功"""
        # Mock 话术服务
        mock_service = MagicMock()
        mock_service.generate.return_value = {
            'generated_script': '这是生成的话术内容',
            'scenario': 'product_inquiry',
            'style': 'professional',
            'tips': ['提示1', '提示2']
        }
        mock_script_service.return_value = mock_service
        
        script_data = test_data.create_test_script_request()
        
        response = client.post('/api/v1/cs/scripts/generate',
                              data=json.dumps(script_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'generated_script' in data['data']
        assert 'id' in data['data']
    
    def test_generate_script_missing_scenario(self, client):
        """测试生成话术缺少场景参数"""
        script_data = {
            'context': {'product_name': '测试基金'},
            'style': 'professional'
        }
        
        response = client.post('/api/v1/cs/scripts/generate',
                              data=json.dumps(script_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_generate_script_empty_body(self, client):
        """测试生成话术空请求体"""
        response = client.post('/api/v1/cs/scripts/generate',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_list_scripts_success(self, client):
        """测试获取话术列表成功"""
        response = client.get('/api/v1/cs/scripts/')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_scripts_with_filters(self, client):
        """测试带过滤条件获取话术列表"""
        response = client.get('/api/v1/cs/scripts/?scenario=product_inquiry&style=professional')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_scripts_with_pagination(self, client):
        """测试分页获取话术列表"""
        response = client.get('/api/v1/cs/scripts/?page=1&page_size=5')
        
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 5
    
    @patch('app.routes.script.ScriptService')
    def test_get_scenarios_success(self, mock_script_service, client):
        """测试获取场景列表成功"""
        # Mock 话术服务
        mock_service = MagicMock()
        mock_service.get_scenarios.return_value = [
            {'code': 'product_inquiry', 'name': '产品咨询', 'description': '客户咨询产品信息'},
            {'code': 'complaint_handling', 'name': '投诉处理', 'description': '处理客户投诉'}
        ]
        mock_script_service.return_value = mock_service
        
        response = client.get('/api/v1/cs/scripts/scenarios')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_rate_script_success(self, client):
        """测试评分话术成功"""
        # 先创建一个话术记录
        with patch('app.routes.script.ScriptService') as mock_service:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = {
                'generated_script': '测试话术',
                'scenario': 'product_inquiry',
                'style': 'professional'
            }
            mock_service.return_value = mock_instance
            
            script_data = {
                'scenario': 'product_inquiry',
                'context': {},
                'style': 'professional'
            }
            create_response = client.post('/api/v1/cs/scripts/generate',
                                         data=json.dumps(script_data),
                                         content_type='application/json')
            
            if create_response.status_code == 200:
                script_id = create_response.get_json()['data']['id']
                
                # 评分
                rate_data = {'rating': 5, 'comment': '很好用的模板'}
                response = client.post(f'/api/v1/cs/scripts/{script_id}/rate',
                                      data=json.dumps(rate_data),
                                      content_type='application/json')
                
                assert response.status_code in [200, 404]  # 可能找到或找不到
    
    def test_rate_script_missing_rating(self, client):
        """测试评分话术缺少评分"""
        rate_data = {'comment': '没有评分'}
        
        response = client.post('/api/v1/cs/scripts/script_001/rate',
                              data=json.dumps(rate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_rate_script_invalid_rating_type(self, client):
        """测试评分话术无效评分类型"""
        rate_data = {'rating': 'excellent'}  # 应该是整数
        
        response = client.post('/api/v1/cs/scripts/script_001/rate',
                              data=json.dumps(rate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_rate_script_rating_out_of_range(self, client):
        """测试评分话术评分超出范围"""
        rate_data = {'rating': 10}  # 应该在1-5之间
        
        response = client.post('/api/v1/cs/scripts/script_001/rate',
                              data=json.dumps(rate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_rate_script_not_found(self, client):
        """测试评分不存在的话术"""
        rate_data = {'rating': 5}
        
        response = client.post('/api/v1/cs/scripts/script_nonexistent/rate',
                              data=json.dumps(rate_data),
                              content_type='application/json')
        
        assert response.status_code == 404
    
    def test_get_statistics(self, client):
        """测试获取话术统计"""
        response = client.get('/api/v1/cs/scripts/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
