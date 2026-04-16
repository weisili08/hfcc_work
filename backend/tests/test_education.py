"""
投教内容接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestEducationEndpoints:
    """投教内容端点测试类"""
    
    def test_list_contents_success(self, client):
        """测试获取投教内容列表成功"""
        response = client.get('/api/v1/education/contents')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_contents_with_filters(self, client):
        """测试带过滤条件获取投教内容"""
        response = client.get('/api/v1/education/contents?category=fund_basics&target_audience=beginner')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_contents_with_keyword_search(self, client):
        """测试关键词搜索投教内容"""
        response = client.get('/api/v1/education/contents?keyword=基金')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_list_contents_invalid_page(self, client):
        """测试无效页码"""
        response = client.get('/api/v1/education/contents?page=0')
        
        assert response.status_code == 400
    
    def test_list_contents_invalid_page_size(self, client):
        """测试无效每页条数"""
        response = client.get('/api/v1/education/contents?page_size=200')
        
        assert response.status_code == 400
    
    def test_create_content_success(self, client, test_data):
        """测试创建投教内容成功"""
        content_data = test_data.create_test_education_content()
        
        response = client.post('/api/v1/education/contents',
                              data=json.dumps(content_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['title'] == content_data['title']
    
    def test_create_content_missing_required_fields(self, client):
        """测试创建投教内容缺少必填字段"""
        content_data = {
            'title': '测试文章'
            # 缺少 category, target_audience, content
        }
        
        response = client.post('/api/v1/education/contents',
                              data=json.dumps(content_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_content_empty_body(self, client):
        """测试创建投教内容空请求体"""
        response = client.post('/api/v1/education/contents',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_content_not_found(self, client):
        """测试获取不存在的投教内容"""
        response = client.get('/api/v1/education/contents/edu_nonexistent')
        
        assert response.status_code == 404
    
    def test_update_content_not_found(self, client):
        """测试更新不存在的投教内容"""
        update_data = {'title': '新标题'}
        
        response = client.put('/api/v1/education/contents/edu_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_update_content_empty_body(self, client):
        """测试更新投教内容空请求体"""
        response = client.put('/api/v1/education/contents/edu_001',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.routes.education.EducationService')
    def test_generate_content_success(self, mock_education_service, client):
        """测试AI生成投教内容成功"""
        # Mock 投教服务
        mock_service = MagicMock()
        mock_service.generate_content.return_value = {
            'title': '生成的标题',
            'content': '生成的内容',
            'outline': ['章节1', '章节2'],
            'key_points': ['要点1', '要点2']
        }
        mock_education_service.return_value = mock_service
        
        generate_data = {
            'topic': '基金入门知识',
            'category': 'fund_basics',
            'target_audience': 'beginner',
            'format': 'article'
        }
        
        response = client.post('/api/v1/education/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_generate_content_missing_topic(self, client):
        """测试AI生成投教内容缺少主题"""
        generate_data = {
            'category': 'fund_basics',
            'target_audience': 'beginner'
        }
        
        response = client.post('/api/v1/education/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_content_missing_category(self, client):
        """测试AI生成投教内容缺少分类"""
        generate_data = {
            'topic': '基金入门知识',
            'target_audience': 'beginner'
        }
        
        response = client.post('/api/v1/education/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_content_missing_target_audience(self, client):
        """测试AI生成投教内容缺少目标受众"""
        generate_data = {
            'topic': '基金入门知识',
            'category': 'fund_basics'
        }
        
        response = client.post('/api/v1/education/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_content_empty_body(self, client):
        """测试AI生成投教内容空请求体"""
        response = client.post('/api/v1/education/generate',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.routes.education.EducationService')
    def test_generate_quiz_success(self, mock_education_service, client):
        """测试生成投教测验成功"""
        # Mock 投教服务
        mock_service = MagicMock()
        mock_service.generate_quiz.return_value = {
            'topic': '基金知识测验',
            'questions': [
                {
                    'question': '什么是基金？',
                    'options': ['A. 选项1', 'B. 选项2', 'C. 选项3', 'D. 选项4'],
                    'answer': 'A',
                    'explanation': '解释'
                }
            ]
        }
        mock_education_service.return_value = mock_service
        
        generate_data = {
            'topic': '基金知识测验',
            'difficulty': 'medium',
            'count': 5
        }
        
        response = client.post('/api/v1/education/quiz/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_generate_quiz_missing_topic(self, client):
        """测试生成投教测验缺少主题"""
        generate_data = {
            'difficulty': 'medium',
            'count': 5
        }
        
        response = client.post('/api/v1/education/quiz/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_quiz_empty_body(self, client):
        """测试生成投教测验空请求体"""
        response = client.post('/api/v1/education/quiz/generate',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_like_content_not_found(self, client):
        """测试点赞不存在的投教内容"""
        response = client.post('/api/v1/education/contents/edu_nonexistent/like')
        
        assert response.status_code == 404
