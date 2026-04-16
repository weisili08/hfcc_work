"""
培训管理接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestTrainingEndpoints:
    """培训管理端点测试类"""
    
    def test_list_trainings_success(self, client):
        """测试获取培训列表成功"""
        response = client.get('/api/v1/cs/training/')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_trainings_with_filters(self, client):
        """测试带过滤条件获取培训列表"""
        response = client.get('/api/v1/cs/training/?type=course&status=published')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_trainings_with_pagination(self, client):
        """测试分页获取培训列表"""
        response = client.get('/api/v1/cs/training/?page=1&page_size=5')
        
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 5
    
    def test_create_training_success(self, client, test_data):
        """测试创建培训成功"""
        training_data = test_data.create_test_training()
        
        response = client.post('/api/v1/cs/training/',
                              data=json.dumps(training_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['title'] == training_data['title']
        assert data['data']['type'] == training_data['type']
        assert 'id' in data['data']
    
    def test_create_training_missing_required_fields(self, client):
        """测试创建培训缺少必填字段"""
        training_data = {
            'title': '测试培训'
            # 缺少 type, category
        }
        
        response = client.post('/api/v1/cs/training/',
                              data=json.dumps(training_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_training_invalid_type(self, client):
        """测试创建培训无效类型"""
        training_data = {
            'title': '测试培训',
            'type': 'invalid_type',  # 无效类型
            'category': '产品知识'
        }
        
        response = client.post('/api/v1/cs/training/',
                              data=json.dumps(training_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_training_invalid_status(self, client):
        """测试创建培训无效状态"""
        training_data = {
            'title': '测试培训',
            'type': 'course',
            'category': '产品知识',
            'status': 'invalid_status'  # 无效状态
        }
        
        response = client.post('/api/v1/cs/training/',
                              data=json.dumps(training_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_training_invalid_difficulty(self, client):
        """测试创建培训无效难度"""
        training_data = {
            'title': '测试培训',
            'type': 'course',
            'category': '产品知识',
            'difficulty': 'expert'  # 无效难度
        }
        
        response = client.post('/api/v1/cs/training/',
                              data=json.dumps(training_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_training_invalid_duration(self, client):
        """测试创建培训无效时长"""
        training_data = {
            'title': '测试培训',
            'type': 'course',
            'category': '产品知识',
            'duration_minutes': 'invalid'  # 应该是整数
        }
        
        response = client.post('/api/v1/cs/training/',
                              data=json.dumps(training_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_training_success(self, client, test_data):
        """测试获取培训详情成功"""
        # 先创建培训
        training_data = test_data.create_test_training()
        create_response = client.post('/api/v1/cs/training/',
                                     data=json.dumps(training_data),
                                     content_type='application/json')
        
        training_id = create_response.get_json()['data']['id']
        
        # 获取详情
        response = client.get(f'/api/v1/cs/training/{training_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == training_id
    
    def test_get_training_not_found(self, client):
        """测试获取不存在的培训"""
        response = client.get('/api/v1/cs/training/training_nonexistent')
        
        assert response.status_code == 404
    
    def test_update_training_success(self, client, test_data):
        """测试更新培训成功"""
        # 先创建培训
        training_data = test_data.create_test_training()
        create_response = client.post('/api/v1/cs/training/',
                                     data=json.dumps(training_data),
                                     content_type='application/json')
        
        training_id = create_response.get_json()['data']['id']
        
        # 更新
        update_data = {
            'title': '更新后的培训标题',
            'description': '更新后的描述'
        }
        response = client.put(f'/api/v1/cs/training/{training_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['title'] == update_data['title']
    
    def test_update_training_not_found(self, client):
        """测试更新不存在的培训"""
        update_data = {'title': '新标题'}
        response = client.put('/api/v1/cs/training/training_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_enroll_training_not_published(self, client, test_data):
        """测试报名未发布的培训"""
        # 先创建草稿状态的培训
        training_data = test_data.create_test_training()
        training_data['status'] = 'draft'
        create_response = client.post('/api/v1/cs/training/',
                                     data=json.dumps(training_data),
                                     content_type='application/json')
        
        training_id = create_response.get_json()['data']['id']
        
        # 尝试报名
        enroll_data = {
            'user_id': 'user_001',
            'user_name': '测试用户'
        }
        response = client.post(f'/api/v1/cs/training/{training_id}/enroll',
                              data=json.dumps(enroll_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_enroll_training_missing_user_id(self, client, test_data):
        """测试报名培训缺少用户ID"""
        # 先创建培训
        training_data = test_data.create_test_training()
        create_response = client.post('/api/v1/cs/training/',
                                     data=json.dumps(training_data),
                                     content_type='application/json')
        
        training_id = create_response.get_json()['data']['id']
        
        # 报名（缺少user_id）
        enroll_data = {'user_name': '测试用户'}
        response = client.post(f'/api/v1/cs/training/{training_id}/enroll',
                              data=json.dumps(enroll_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.routes.training.TrainingService')
    def test_generate_content_success(self, mock_training_service, client):
        """测试AI生成培训内容成功"""
        # Mock 培训服务
        mock_service = MagicMock()
        mock_service.generate_content.return_value = {
            'title': '生成的培训标题',
            'content': '生成的培训内容',
            'outline': ['章节1', '章节2'],
            'key_points': ['要点1', '要点2']
        }
        mock_training_service.return_value = mock_service
        
        generate_data = {
            'topic': '基金基础知识',
            'difficulty': 'beginner'
        }
        
        response = client.post('/api/v1/cs/training/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_generate_content_missing_topic(self, client):
        """测试AI生成培训内容缺少主题"""
        generate_data = {
            'difficulty': 'beginner'
        }
        
        response = client.post('/api/v1/cs/training/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_content_invalid_difficulty(self, client):
        """测试AI生成培训内容无效难度"""
        generate_data = {
            'topic': '基金基础知识',
            'difficulty': 'expert'  # 无效难度
        }
        
        response = client.post('/api/v1/cs/training/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.routes.training.TrainingService')
    def test_generate_exam_success(self, mock_training_service, client):
        """测试AI生成考核试题成功"""
        # Mock 培训服务
        mock_service = MagicMock()
        mock_service.generate_exam.return_value = {
            'topic': '基金知识考核',
            'questions': [
                {'question': '问题1', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A'}
            ]
        }
        mock_training_service.return_value = mock_service
        
        generate_data = {
            'topic': '基金知识考核',
            'question_count': 10
        }
        
        response = client.post('/api/v1/cs/training/exam/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_generate_exam_missing_topic(self, client):
        """测试AI生成考核试题缺少主题"""
        generate_data = {
            'question_count': 10
        }
        
        response = client.post('/api/v1/cs/training/exam/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_exam_invalid_question_count(self, client):
        """测试AI生成考核试题无效题目数量"""
        generate_data = {
            'topic': '基金知识考核',
            'question_count': 'invalid'  # 应该是整数
        }
        
        response = client.post('/api/v1/cs/training/exam/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_exam_question_count_out_of_range(self, client):
        """测试AI生成考核试题题目数量超出范围"""
        generate_data = {
            'topic': '基金知识考核',
            'question_count': 100  # 超出5-50范围
        }
        
        response = client.post('/api/v1/cs/training/exam/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_list_records_success(self, client):
        """测试获取培训记录列表成功"""
        response = client.get('/api/v1/cs/training/records')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_statistics(self, client):
        """测试获取培训统计"""
        response = client.get('/api/v1/cs/training/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
