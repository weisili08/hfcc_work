"""
智能问答接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestQAEndpoints:
    """智能问答端点测试类"""
    
    @patch('app.routes.qa.QAService')
    def test_ask_question_success(self, mock_qa_service, client, auth_headers):
        """测试提问成功"""
        # Mock QA服务
        mock_service = MagicMock()
        mock_service.ask.return_value = {
            'answer': '这是测试回答',
            'sources': [],
            'confidence': 0.85,
            'answer_source': 'fallback',
            'session_id': 'test_session',
            'response_time_ms': 100
        }
        mock_qa_service.return_value = mock_service
        
        ask_data = {
            'query': '什么是基金？',
            'session_id': None
        }
        
        response = client.post('/api/v1/cs/qa/ask',
                              data=json.dumps(ask_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'answer' in data['data']
    
    def test_ask_question_missing_query(self, client, auth_headers):
        """测试提问缺少问题内容"""
        ask_data = {
            'session_id': None
        }
        
        response = client.post('/api/v1/cs/qa/ask',
                              data=json.dumps(ask_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_ask_question_empty_body(self, client, auth_headers):
        """测试提问空请求体"""
        response = client.post('/api/v1/cs/qa/ask',
                              data=json.dumps({}),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_ask_question_without_auth(self, client):
        """测试未认证提问"""
        ask_data = {'query': '测试问题'}
        response = client.post('/api/v1/cs/qa/ask',
                              data=json.dumps(ask_data),
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_list_sessions_success(self, client, auth_headers):
        """测试获取会话列表成功"""
        response = client.get('/api/v1/cs/qa/sessions',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_sessions_without_auth(self, client):
        """测试未认证获取会话列表"""
        response = client.get('/api/v1/cs/qa/sessions')
        
        assert response.status_code == 401
    
    def test_list_sessions_with_pagination(self, client, auth_headers):
        """测试分页获取会话列表"""
        response = client.get('/api/v1/cs/qa/sessions?page=1&page_size=10',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 10
    
    def test_get_session_not_found(self, client, auth_headers):
        """测试获取不存在的会话"""
        response = client.get('/api/v1/cs/qa/sessions/session_nonexistent',
                             headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_session_not_found(self, client, auth_headers):
        """测试删除不存在的会话"""
        response = client.delete('/api/v1/cs/qa/sessions/session_nonexistent',
                                headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_add_feedback_missing_record_id(self, client, auth_headers):
        """测试添加反馈缺少记录ID"""
        feedback_data = {
            'rating': 5
        }
        
        response = client.post('/api/v1/cs/qa/feedback',
                              data=json.dumps(feedback_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_add_feedback_invalid_rating(self, client, auth_headers):
        """测试添加反馈无效评分"""
        feedback_data = {
            'record_id': 'record_001',
            'rating': 10  # 超出范围
        }
        
        response = client.post('/api/v1/cs/qa/feedback',
                              data=json.dumps(feedback_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_add_feedback_without_auth(self, client):
        """测试未认证添加反馈"""
        feedback_data = {
            'record_id': 'record_001',
            'rating': 5
        }
        
        response = client.post('/api/v1/cs/qa/feedback',
                              data=json.dumps(feedback_data),
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_get_session_statistics_not_found(self, client, auth_headers):
        """测试获取不存在会话的统计信息"""
        response = client.get('/api/v1/cs/qa/sessions/session_nonexistent/statistics',
                             headers=auth_headers)
        
        assert response.status_code == 404
