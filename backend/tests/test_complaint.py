"""
投诉管理接口测试
"""

import pytest
import json


class TestComplaintEndpoints:
    """投诉管理端点测试类"""
    
    def test_list_complaints_success(self, client):
        """测试获取投诉列表成功"""
        response = client.get('/api/v1/cs/complaints/')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_complaints_with_filters(self, client):
        """测试带过滤条件的投诉列表"""
        response = client.get('/api/v1/cs/complaints/?status=pending&priority=high')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_complaints_with_pagination(self, client):
        """测试分页获取投诉列表"""
        response = client.get('/api/v1/cs/complaints/?page=1&page_size=5')
        
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 5
    
    def test_create_complaint_success(self, client, test_data):
        """测试创建投诉成功"""
        complaint_data = test_data.create_test_complaint()
        
        response = client.post('/api/v1/cs/complaints/',
                              data=json.dumps(complaint_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['title'] == complaint_data['title']
        assert data['data']['status'] == 'pending'
        assert 'id' in data['data']
    
    def test_create_complaint_missing_required_fields(self, client):
        """测试创建投诉缺少必填字段"""
        complaint_data = {
            'title': '缺少必填字段的投诉'
            # 缺少 customer_name, type, description
        }
        
        response = client.post('/api/v1/cs/complaints/',
                              data=json.dumps(complaint_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_complaint_invalid_type(self, client):
        """测试创建投诉无效类型"""
        complaint_data = {
            'title': '测试投诉',
            'customer_name': '测试客户',
            'type': 'invalid_type',  # 无效类型
            'description': '测试描述'
        }
        
        response = client.post('/api/v1/cs/complaints/',
                              data=json.dumps(complaint_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_complaint_invalid_priority(self, client):
        """测试创建投诉无效优先级"""
        complaint_data = {
            'title': '测试投诉',
            'customer_name': '测试客户',
            'type': 'product',
            'description': '测试描述',
            'priority': 'urgent'  # 无效优先级
        }
        
        response = client.post('/api/v1/cs/complaints/',
                              data=json.dumps(complaint_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_complaint_success(self, client, test_data):
        """测试获取投诉详情成功"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 获取详情
        response = client.get(f'/api/v1/cs/complaints/{complaint_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == complaint_id
    
    def test_get_complaint_not_found(self, client):
        """测试获取不存在的投诉"""
        response = client.get('/api/v1/cs/complaints/tk_nonexistent')
        
        assert response.status_code == 404
    
    def test_update_complaint_success(self, client, test_data):
        """测试更新投诉成功"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 更新
        update_data = {
            'title': '更新后的投诉标题',
            'priority': 'medium'
        }
        response = client.put(f'/api/v1/cs/complaints/{complaint_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['title'] == update_data['title']
    
    def test_update_complaint_not_found(self, client):
        """测试更新不存在的投诉"""
        update_data = {'title': '新标题'}
        response = client.put('/api/v1/cs/complaints/tk_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_assign_complaint_success(self, client, test_data):
        """测试分配投诉成功"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 分配
        assign_data = {'assignee': '客服专员A'}
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/assign',
                              data=json.dumps(assign_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['assignee'] == '客服专员A'
    
    def test_assign_complaint_missing_assignee(self, client, test_data):
        """测试分配投诉缺少处理人"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 分配（缺少assignee）
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/assign',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_escalate_complaint_success(self, client, test_data):
        """测试升级投诉成功"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 升级
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/escalate')
        
        assert response.status_code == 200
    
    def test_escalate_resolved_complaint(self, client, test_data):
        """测试升级已解决的投诉（应该失败）"""
        # 先创建并解决投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 先解决
        client.post(f'/api/v1/cs/complaints/{complaint_id}/resolve',
                   data=json.dumps({'resolution': '已解决'}),
                   content_type='application/json')
        
        # 尝试升级
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/escalate')
        
        # 已解决的投诉不能升级
        assert response.status_code == 400
    
    def test_resolve_complaint_success(self, client, test_data):
        """测试解决投诉成功"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 解决
        resolve_data = {'resolution': '已与客户沟通并解决问题'}
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/resolve',
                              data=json.dumps(resolve_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'resolved'
    
    def test_resolve_complaint_missing_resolution(self, client, test_data):
        """测试解决投诉缺少解决方案"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 解决（缺少resolution）
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/resolve',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_close_complaint_success(self, client, test_data):
        """测试关闭投诉成功"""
        # 先创建投诉
        complaint_data = test_data.create_test_complaint()
        create_response = client.post('/api/v1/cs/complaints/',
                                     data=json.dumps(complaint_data),
                                     content_type='application/json')
        
        complaint_id = create_response.get_json()['data']['id']
        
        # 关闭
        response = client.post(f'/api/v1/cs/complaints/{complaint_id}/close')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'closed'
    
    def test_get_statistics(self, client):
        """测试获取投诉统计"""
        response = client.get('/api/v1/cs/complaints/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
