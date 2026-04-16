"""
质检管理接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestQualityEndpoints:
    """质检管理端点测试类"""
    
    def test_list_checks_success(self, client):
        """测试获取质检记录列表成功"""
        response = client.get('/api/v1/cs/quality/checks')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_checks_with_filters(self, client):
        """测试带过滤条件获取质检记录"""
        response = client.get('/api/v1/cs/quality/checks?status=pending&agent_name=测试客服')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_checks_with_pagination(self, client):
        """测试分页获取质检记录"""
        response = client.get('/api/v1/cs/quality/checks?page=1&page_size=5')
        
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 5
    
    def test_create_check_success(self, client, test_data):
        """测试创建质检记录成功"""
        check_data = test_data.create_test_quality_check()
        
        response = client.post('/api/v1/cs/quality/checks',
                              data=json.dumps(check_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['agent_name'] == check_data['agent_name']
        assert data['data']['status'] == 'pending'
        assert 'id' in data['data']
    
    def test_create_check_missing_required_fields(self, client):
        """测试创建质检记录缺少必填字段"""
        check_data = {
            'agent_name': '测试客服'
            # 缺少 call_date, call_content
        }
        
        response = client.post('/api/v1/cs/quality/checks',
                              data=json.dumps(check_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_check_invalid_duration(self, client):
        """测试创建质检记录无效通话时长"""
        check_data = {
            'agent_name': '测试客服',
            'call_date': '2026-04-15',
            'call_content': '测试通话内容',
            'call_duration': 'invalid'  # 应该是整数
        }
        
        response = client.post('/api/v1/cs/quality/checks',
                              data=json.dumps(check_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_check_empty_body(self, client):
        """测试创建质检记录空请求体"""
        response = client.post('/api/v1/cs/quality/checks',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_check_success(self, client, test_data):
        """测试获取质检详情成功"""
        # 先创建质检记录
        check_data = test_data.create_test_quality_check()
        create_response = client.post('/api/v1/cs/quality/checks',
                                     data=json.dumps(check_data),
                                     content_type='application/json')
        
        check_id = create_response.get_json()['data']['id']
        
        # 获取详情
        response = client.get(f'/api/v1/cs/quality/checks/{check_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == check_id
    
    def test_get_check_not_found(self, client):
        """测试获取不存在的质检记录"""
        response = client.get('/api/v1/cs/quality/checks/qc_nonexistent')
        
        assert response.status_code == 404
    
    @patch('app.routes.quality.QualityService')
    def test_analyze_call_success(self, mock_quality_service, client):
        """测试AI质检分析成功"""
        # Mock 质检服务
        mock_service = MagicMock()
        mock_service.analyze.return_value = {
            'overall_score': 85,
            'scores': {
                'courtesy': 90,
                'accuracy': 85,
                'completeness': 80
            },
            'issues': [],
            'suggestions': ['建议1', '建议2']
        }
        mock_quality_service.return_value = mock_service
        
        analyze_data = {
            'call_content': '客户：我想了解基金产品。客服：您好，请问有什么可以帮您？',
            'agent_name': '测试客服'
        }
        
        response = client.post('/api/v1/cs/quality/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'overall_score' in data['data']
    
    def test_analyze_call_missing_content(self, client):
        """测试AI质检分析缺少通话内容"""
        analyze_data = {
            'agent_name': '测试客服'
        }
        
        response = client.post('/api/v1/cs/quality/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_analyze_call_content_too_short(self, client):
        """测试AI质检分析通话内容太短"""
        analyze_data = {
            'call_content': '你好',  # 少于10个字符
            'agent_name': '测试客服'
        }
        
        response = client.post('/api/v1/cs/quality/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_analyze_call_empty_body(self, client):
        """测试AI质检分析空请求体"""
        response = client.post('/api/v1/cs/quality/analyze',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_statistics(self, client):
        """测试获取质检统计"""
        response = client.get('/api/v1/cs/quality/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_get_statistics_with_date_range(self, client):
        """测试带日期范围的质检统计"""
        response = client.get('/api/v1/cs/quality/statistics?start_date=2026-04-01&end_date=2026-04-30')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_get_agent_statistics(self, client):
        """测试获取指定客服的质检统计"""
        response = client.get('/api/v1/cs/quality/agents/测试客服/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
