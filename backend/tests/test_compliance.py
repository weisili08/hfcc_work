"""
合规检查接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestComplianceEndpoints:
    """合规检查端点测试类"""
    
    def test_list_checks_success(self, client):
        """测试获取合规检查记录列表成功"""
        response = client.get('/api/v1/compliance/checks')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_checks_with_filters(self, client):
        """测试带过滤条件获取合规检查记录"""
        response = client.get('/api/v1/compliance/checks?check_type=content&result=pass')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_checks_invalid_page(self, client):
        """测试无效页码"""
        response = client.get('/api/v1/compliance/checks?page=0')
        
        assert response.status_code == 400
    
    def test_list_checks_invalid_page_size(self, client):
        """测试无效每页条数"""
        response = client.get('/api/v1/compliance/checks?page_size=200')
        
        assert response.status_code == 400
    
    @patch('app.routes.compliance.ComplianceService')
    def test_check_content_success(self, mock_compliance_service, client):
        """测试AI合规检查成功"""
        # Mock 合规服务
        mock_service = MagicMock()
        mock_service.check_content.return_value = {
            'result': 'pass',
            'risk_level': 'low',
            'issues': [],
            'suggestions': []
        }
        mock_compliance_service.return_value = mock_service
        
        check_data = {
            'content': '这是一段需要检查的文本内容',
            'check_type': 'content'
        }
        
        response = client.post('/api/v1/compliance/check',
                              data=json.dumps(check_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_check_content_missing_content(self, client):
        """测试AI合规检查缺少内容"""
        check_data = {
            'check_type': 'content'
        }
        
        response = client.post('/api/v1/compliance/check',
                              data=json.dumps(check_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_check_content_empty_body(self, client):
        """测试AI合规检查空请求体"""
        response = client.post('/api/v1/compliance/check',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_check_content_invalid_check_type(self, client):
        """测试AI合规检查无效检查类型"""
        check_data = {
            'content': '检查内容',
            'check_type': 'invalid_type'  # 无效类型
        }
        
        response = client.post('/api/v1/compliance/check',
                              data=json.dumps(check_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_check_not_found(self, client):
        """测试获取不存在的合规检查记录"""
        response = client.get('/api/v1/compliance/checks/check_nonexistent')
        
        assert response.status_code == 404
    
    @patch('app.routes.compliance.ComplianceService')
    def test_check_aml_success(self, mock_compliance_service, client):
        """测试反洗钱检查成功"""
        # Mock 合规服务
        mock_service = MagicMock()
        mock_service.check_aml.return_value = {
            'result': 'pass',
            'risk_level': 'low',
            'alerts': [],
            'recommendations': []
        }
        mock_compliance_service.return_value = mock_service
        
        aml_data = {
            'customer_id': 'cp_001',
            'transaction_amount': 10000,
            'transaction_type': '普通交易',
            'counterparty': '对手方',
            'frequency': '正常'
        }
        
        response = client.post('/api/v1/compliance/aml/check',
                              data=json.dumps(aml_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_check_aml_missing_transaction_amount(self, client):
        """测试反洗钱检查缺少交易金额"""
        aml_data = {
            'customer_id': 'cp_001',
            'transaction_type': '普通交易'
        }
        
        response = client.post('/api/v1/compliance/aml/check',
                              data=json.dumps(aml_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_check_aml_empty_body(self, client):
        """测试反洗钱检查空请求体"""
        response = client.post('/api/v1/compliance/aml/check',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_risk_tips_success(self, client):
        """测试获取合规风险提示成功"""
        response = client.get('/api/v1/compliance/risk-tips')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'tips' in data['data']
    
    def test_get_risk_tips_with_filters(self, client):
        """测试带过滤条件获取合规风险提示"""
        response = client.get('/api/v1/compliance/risk-tips?scenario=产品销售')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'tips' in data['data']
    
    def test_get_statistics(self, client):
        """测试获取合规统计"""
        response = client.get('/api/v1/compliance/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_get_rules(self, client):
        """测试获取合规规则列表"""
        response = client.get('/api/v1/compliance/rules')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'rules' in data['data']
