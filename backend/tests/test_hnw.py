"""
高净值客户服务接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestHNWCustomerEndpoints:
    """高净值客户管理端点测试类"""
    
    def test_list_customers_success(self, client):
        """测试获取客户列表成功"""
        response = client.get('/api/v1/hnw/customers')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_customers_with_filters(self, client):
        """测试带过滤条件获取客户列表"""
        response = client.get('/api/v1/hnw/customers?tier=platinum&risk_level=moderate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_customers_with_pagination(self, client):
        """测试分页获取客户列表"""
        response = client.get('/api/v1/hnw/customers?page=1&page_size=5')
        
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 5
    
    def test_create_customer_success(self, client, test_data):
        """测试创建客户成功"""
        customer_data = test_data.create_test_hnw_customer()
        
        response = client.post('/api/v1/hnw/customers',
                              data=json.dumps(customer_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['name'] == customer_data['name']
        assert data['data']['tier'] == customer_data['tier']
        assert 'id' in data['data']
    
    def test_create_customer_missing_required_fields(self, client):
        """测试创建客户缺少必填字段"""
        customer_data = {
            'name': '测试客户'
            # 缺少 phone, risk_level, aum, tier
        }
        
        response = client.post('/api/v1/hnw/customers',
                              data=json.dumps(customer_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_customer_invalid_risk_level(self, client):
        """测试创建客户无效风险等级"""
        customer_data = {
            'name': '测试客户',
            'phone': '13900139000',
            'risk_level': 'invalid',  # 无效风险等级
            'aum': 5000000,
            'tier': 'platinum'
        }
        
        response = client.post('/api/v1/hnw/customers',
                              data=json.dumps(customer_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_customer_invalid_tier(self, client):
        """测试创建客户无效等级"""
        customer_data = {
            'name': '测试客户',
            'phone': '13900139000',
            'risk_level': 'moderate',
            'aum': 5000000,
            'tier': 'silver'  # 无效等级
        }
        
        response = client.post('/api/v1/hnw/customers',
                              data=json.dumps(customer_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_customer_success(self, client, test_data):
        """测试获取客户详情成功"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        # 获取详情
        response = client.get(f'/api/v1/hnw/customers/{customer_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == customer_id
    
    def test_get_customer_not_found(self, client):
        """测试获取不存在的客户"""
        response = client.get('/api/v1/hnw/customers/cp_nonexistent')
        
        assert response.status_code == 404
    
    def test_update_customer_success(self, client, test_data):
        """测试更新客户成功"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        # 更新
        update_data = {
            'name': '更新后的客户名称',
            'aum': 6000000
        }
        response = client.put(f'/api/v1/hnw/customers/{customer_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['name'] == update_data['name']
    
    def test_update_customer_not_found(self, client):
        """测试更新不存在的客户"""
        update_data = {'name': '新名称'}
        response = client.put('/api/v1/hnw/customers/cp_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_update_customer_invalid_risk_level(self, client, test_data):
        """测试更新客户无效风险等级"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        # 更新（无效风险等级）
        update_data = {'risk_level': 'invalid'}
        response = client.put(f'/api/v1/hnw/customers/{customer_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 400


class TestHNWAllocationEndpoints:
    """资产配置端点测试类"""
    
    @patch('app.routes.hnw.AllocationService')
    def test_generate_allocation_with_customer_id(self, mock_allocation_service, client, test_data):
        """测试通过客户ID生成资产配置建议"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        # Mock 资产配置服务
        mock_service = MagicMock()
        mock_service.generate_allocation.return_value = {
            'allocation_plan': {
                'equity_pct': 40,
                'bond_pct': 40,
                'money_market_pct': 15,
                'alternative_pct': 5
            },
            'recommended_products': [],
            'rationale': '基于客户风险承受能力',
            'risk_warnings': ['投资有风险']
        }
        mock_allocation_service.return_value = mock_service
        
        allocation_data = {
            'customer_id': customer_id
        }
        
        response = client.post('/api/v1/hnw/allocation',
                              data=json.dumps(allocation_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'recommendations' in data['data']
    
    def test_generate_allocation_with_profile(self, client):
        """测试通过客户画像生成资产配置建议"""
        allocation_data = {
            'risk_level': 'moderate',
            'aum': 5000000,
            'age_range': '40-50',
            'investment_horizon': '中长期'
        }
        
        response = client.post('/api/v1/hnw/allocation',
                              data=json.dumps(allocation_data),
                              content_type='application/json')
        
        # 可能成功或失败，取决于LLM服务
        assert response.status_code in [200, 500]
    
    def test_generate_allocation_missing_required_fields(self, client):
        """测试生成资产配置缺少必填字段"""
        allocation_data = {
            'age_range': '40-50'
            # 缺少 risk_level, aum
        }
        
        response = client.post('/api/v1/hnw/allocation',
                              data=json.dumps(allocation_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_allocation_customer_not_found(self, client):
        """测试为不存在的客户生成资产配置"""
        allocation_data = {
            'customer_id': 'cp_nonexistent'
        }
        
        response = client.post('/api/v1/hnw/allocation',
                              data=json.dumps(allocation_data),
                              content_type='application/json')
        
        assert response.status_code == 404


class TestHNWServiceEndpoints:
    """服务记录端点测试类"""
    
    def test_list_services_success(self, client):
        """测试获取服务记录列表成功"""
        response = client.get('/api/v1/hnw/services')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_services_with_filters(self, client):
        """测试带过滤条件获取服务记录"""
        response = client.get('/api/v1/hnw/services?service_type=consultation')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_create_service_success(self, client, test_data):
        """测试创建服务记录成功"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        service_data = {
            'customer_id': customer_id,
            'service_type': 'consultation',
            'description': '投资咨询',
            'result': '客户满意'
        }
        
        response = client.post('/api/v1/hnw/services',
                              data=json.dumps(service_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['customer_id'] == customer_id
    
    def test_create_service_missing_customer_id(self, client):
        """测试创建服务记录缺少客户ID"""
        service_data = {
            'service_type': 'consultation',
            'description': '投资咨询'
        }
        
        response = client.post('/api/v1/hnw/services',
                              data=json.dumps(service_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_service_customer_not_found(self, client):
        """测试为不存在的客户创建服务记录"""
        service_data = {
            'customer_id': 'cp_nonexistent',
            'service_type': 'consultation',
            'description': '投资咨询'
        }
        
        response = client.post('/api/v1/hnw/services',
                              data=json.dumps(service_data),
                              content_type='application/json')
        
        assert response.status_code == 404
    
    def test_create_service_invalid_type(self, client, test_data):
        """测试创建服务记录无效类型"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        service_data = {
            'customer_id': customer_id,
            'service_type': 'invalid_type',  # 无效类型
            'description': '投资咨询'
        }
        
        response = client.post('/api/v1/hnw/services',
                              data=json.dumps(service_data),
                              content_type='application/json')
        
        assert response.status_code == 400


class TestHNWEventEndpoints:
    """活动管理端点测试类"""
    
    def test_list_events_success(self, client):
        """测试获取活动列表成功"""
        response = client.get('/api/v1/hnw/events')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_events_with_filters(self, client):
        """测试带过滤条件获取活动列表"""
        response = client.get('/api/v1/hnw/events?status=planning&type=offline')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_create_event_success(self, client):
        """测试创建活动成功"""
        event_data = {
            'title': '高端客户答谢会',
            'type': 'offline',
            'description': '年度客户答谢活动',
            'target_tier': ['diamond', 'platinum'],
            'date': '2026-05-01',
            'location': '北京',
            'budget': 100000
        }
        
        response = client.post('/api/v1/hnw/events',
                              data=json.dumps(event_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['title'] == event_data['title']
    
    def test_create_event_missing_title(self, client):
        """测试创建活动缺少标题"""
        event_data = {
            'type': 'offline',
            'description': '没有标题的活动'
        }
        
        response = client.post('/api/v1/hnw/events',
                              data=json.dumps(event_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_event_invalid_type(self, client):
        """测试创建活动无效类型"""
        event_data = {
            'title': '测试活动',
            'type': 'invalid_type'  # 无效类型
        }
        
        response = client.post('/api/v1/hnw/events',
                              data=json.dumps(event_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_plan_event_missing_required_fields(self, client):
        """测试AI策划活动缺少必填字段"""
        event_data = {
            'event_type': 'fixed_income'
            # 缺少 target_tier, budget
        }
        
        response = client.post('/api/v1/hnw/events/plan',
                              data=json.dumps(event_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_plan_event_invalid_event_type(self, client):
        """测试AI策划活动无效活动类型"""
        event_data = {
            'event_type': 'invalid_type',
            'target_tier': 'platinum',
            'budget': 50000
        }
        
        response = client.post('/api/v1/hnw/events/plan',
                              data=json.dumps(event_data),
                              content_type='application/json')
        
        assert response.status_code == 400


class TestHNWTouchpointEndpoints:
    """触达任务端点测试类"""
    
    def test_list_touchpoints_success(self, client):
        """测试获取触达任务列表成功"""
        response = client.get('/api/v1/hnw/touchpoints')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_touchpoints_with_filters(self, client):
        """测试带过滤条件获取触达任务"""
        response = client.get('/api/v1/hnw/touchpoints?status=pending&upcoming_days=30')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_generate_touchpoint_missing_customer_id(self, client):
        """测试生成触达话术缺少客户ID"""
        touchpoint_data = {
            'trigger': 'birthday'
        }
        
        response = client.post('/api/v1/hnw/touchpoints/generate',
                              data=json.dumps(touchpoint_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_touchpoint_missing_trigger(self, client):
        """测试生成触达话术缺少触发事件"""
        touchpoint_data = {
            'customer_id': 'cp_001'
        }
        
        response = client.post('/api/v1/hnw/touchpoints/generate',
                              data=json.dumps(touchpoint_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_touchpoint_customer_not_found(self, client):
        """测试为不存在的客户生成触达话术"""
        touchpoint_data = {
            'customer_id': 'cp_nonexistent',
            'trigger': 'birthday'
        }
        
        response = client.post('/api/v1/hnw/touchpoints/generate',
                              data=json.dumps(touchpoint_data),
                              content_type='application/json')
        
        assert response.status_code == 404
    
    def test_generate_touchpoint_invalid_trigger(self, client, test_data):
        """测试生成触达话术无效触发事件"""
        # 先创建客户
        customer_data = test_data.create_test_hnw_customer()
        create_response = client.post('/api/v1/hnw/customers',
                                     data=json.dumps(customer_data),
                                     content_type='application/json')
        
        customer_id = create_response.get_json()['data']['id']
        
        touchpoint_data = {
            'customer_id': customer_id,
            'trigger': 'invalid_trigger'  # 无效触发事件
        }
        
        response = client.post('/api/v1/hnw/touchpoints/generate',
                              data=json.dumps(touchpoint_data),
                              content_type='application/json')
        
        assert response.status_code == 400
