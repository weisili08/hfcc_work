"""
数据分析接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestProfileEndpoints:
    """客户画像端点测试类"""
    
    def test_list_profiles_success(self, client):
        """测试获取客户画像列表成功"""
        response = client.get('/api/v1/analytics/profiles')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_profiles_with_filters(self, client):
        """测试带过滤条件获取客户画像"""
        response = client.get('/api/v1/analytics/profiles?value_tier=high')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_profiles_with_tag_filter(self, client):
        """测试按标签筛选客户画像"""
        response = client.get('/api/v1/analytics/profiles?tag=高价值')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_get_profile_not_found(self, client):
        """测试获取不存在的客户画像"""
        response = client.get('/api/v1/analytics/profiles/cp_nonexistent')
        
        assert response.status_code == 404
    
    def test_analyze_profile_missing_customer_data(self, client):
        """测试AI分析客户画像缺少客户数据"""
        analyze_data = {
            'save': False
        }
        
        response = client.post('/api/v1/analytics/profiles/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_similar_profiles_not_found(self, client):
        """测试获取相似客户（画像不存在）"""
        response = client.get('/api/v1/analytics/profiles/cp_nonexistent/similar')
        
        # 可能返回404或空列表
        assert response.status_code in [200, 404]
    
    def test_get_profile_insights_not_found(self, client):
        """测试获取客户洞察（画像不存在）"""
        response = client.get('/api/v1/analytics/profiles/cp_nonexistent/insights')
        
        assert response.status_code == 404
    
    def test_get_profile_tags(self, client):
        """测试获取标签体系"""
        response = client.get('/api/v1/analytics/profiles/tags')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data


class TestAnomalyEndpoints:
    """异常识别端点测试类"""
    
    def test_list_anomalies_success(self, client):
        """测试获取异常告警列表成功"""
        response = client.get('/api/v1/analytics/anomalies')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_anomalies_with_filters(self, client):
        """测试带过滤条件获取异常告警"""
        response = client.get('/api/v1/analytics/anomalies?severity=high&status=new')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_get_anomaly_not_found(self, client):
        """测试获取不存在的异常告警"""
        response = client.get('/api/v1/analytics/anomalies/alt_nonexistent')
        
        assert response.status_code == 404
    
    def test_detect_anomaly_missing_transaction_data(self, client):
        """测试异常检测缺少交易数据"""
        detect_data = {
            'customer_id': 'cp_001',
            'customer_name': '测试客户'
        }
        
        response = client.post('/api/v1/analytics/anomalies/detect',
                              data=json.dumps(detect_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_detect_anomaly_empty_body(self, client):
        """测试异常检测空请求体"""
        response = client.post('/api/v1/analytics/anomalies/detect',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_analyze_anomaly_not_found(self, client):
        """测试AI分析异常（告警不存在）"""
        response = client.post('/api/v1/analytics/anomalies/alt_nonexistent/analyze')
        
        assert response.status_code in [404, 500]
    
    def test_update_anomaly_status_missing_status(self, client):
        """测试更新告警状态缺少状态参数"""
        update_data = {
            'analysis': '分析结果'
        }
        
        response = client.put('/api/v1/analytics/anomalies/alt_001',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_update_anomaly_status_not_found(self, client):
        """测试更新不存在的告警状态"""
        update_data = {'status': 'resolved'}
        
        response = client.put('/api/v1/analytics/anomalies/alt_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_get_anomaly_statistics(self, client):
        """测试获取异常统计"""
        response = client.get('/api/v1/analytics/anomalies/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data


class TestChurnEndpoints:
    """流失预警端点测试类"""
    
    def test_list_churn_risks_success(self, client):
        """测试获取流失预警列表成功"""
        response = client.get('/api/v1/analytics/churn/risks')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_churn_risks_with_filters(self, client):
        """测试带过滤条件获取流失预警"""
        response = client.get('/api/v1/analytics/churn/risks?risk_level=high&status=new')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_predict_churn_empty_body(self, client):
        """测试流失预测空请求体"""
        response = client.post('/api/v1/analytics/churn/predict',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 200  # 可能返回空预测结果
    
    def test_generate_retention_plan_not_found(self, client):
        """测试生成挽留建议（风险记录不存在）"""
        response = client.post('/api/v1/analytics/churn/risks/cr_nonexistent/retention')
        
        assert response.status_code == 404
    
    def test_update_churn_status_missing_status(self, client):
        """测试更新流失风险状态缺少状态参数"""
        update_data = {
            'note': '备注信息'
        }
        
        response = client.put('/api/v1/analytics/churn/risks/cr_001',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_update_churn_status_not_found(self, client):
        """测试更新不存在的流失风险状态"""
        update_data = {'status': 'contacted'}
        
        response = client.put('/api/v1/analytics/churn/risks/cr_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_get_churn_statistics(self, client):
        """测试获取流失预警统计"""
        response = client.get('/api/v1/analytics/churn/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data


class TestReportEndpoints:
    """报表服务端点测试类"""
    
    def test_list_reports_success(self, client):
        """测试获取报表列表成功"""
        response = client.get('/api/v1/analytics/reports')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_reports_with_filters(self, client):
        """测试带过滤条件获取报表"""
        response = client.get('/api/v1/analytics/reports?type=daily&category=service')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_get_report_not_found(self, client):
        """测试获取不存在的报表"""
        response = client.get('/api/v1/analytics/reports/rpt_nonexistent')
        
        assert response.status_code == 404
    
    def test_create_report_missing_title(self, client):
        """测试创建报表缺少标题"""
        report_data = {
            'type': 'daily',
            'category': 'service'
        }
        
        response = client.post('/api/v1/analytics/reports',
                              data=json.dumps(report_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_report_missing_type(self, client):
        """测试创建报表缺少类型"""
        report_data = {
            'title': '测试报表',
            'category': 'service'
        }
        
        response = client.post('/api/v1/analytics/reports',
                              data=json.dumps(report_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_create_report_empty_body(self, client):
        """测试创建报表空请求体"""
        response = client.post('/api/v1/analytics/reports',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_generate_report_missing_type(self, client):
        """测试AI生成报表缺少类型"""
        generate_data = {
            'category': 'service',
            'parameters': {}
        }
        
        response = client.post('/api/v1/analytics/reports/generate',
                              data=json.dumps(generate_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_report_summary_not_found(self, client):
        """测试获取报表AI摘要（报表不存在）"""
        response = client.get('/api/v1/analytics/reports/rpt_nonexistent/summary')
        
        assert response.status_code == 404
    
    def test_get_report_statistics(self, client):
        """测试获取报表统计"""
        response = client.get('/api/v1/analytics/reports/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
