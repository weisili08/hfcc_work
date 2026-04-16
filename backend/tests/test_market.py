"""
市场监测接口测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestSentimentEndpoints:
    """舆情监控端点测试类"""
    
    def test_list_sentiment_success(self, client):
        """测试获取舆情列表成功"""
        response = client.get('/api/v1/market/sentiment')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_sentiment_with_filters(self, client):
        """测试带过滤条件获取舆情列表"""
        response = client.get('/api/v1/market/sentiment?sentiment=negative&severity=high')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_sentiment_invalid_page(self, client):
        """测试无效页码"""
        response = client.get('/api/v1/market/sentiment?page=0')
        
        assert response.status_code == 400
    
    def test_list_sentiment_invalid_page_size(self, client):
        """测试无效每页条数"""
        response = client.get('/api/v1/market/sentiment?page_size=200')
        
        assert response.status_code == 400
    
    @patch('app.routes.market.SentimentService')
    def test_analyze_sentiment_success(self, mock_sentiment_service, client):
        """测试AI舆情分析成功"""
        # Mock 舆情服务
        mock_service = MagicMock()
        mock_service.analyze.return_value = {
            'sentiment': 'neutral',
            'severity': 'low',
            'keywords': ['基金', '市场'],
            'related_products': ['XX基金'],
            'alert_level': 'normal'
        }
        mock_service.save_record.return_value = {'id': 'sen_001'}
        mock_sentiment_service.return_value = mock_service
        
        analyze_data = {
            'content': '今天市场表现平稳，基金净值小幅上涨。',
            'source': '新闻',
            'title': '市场动态'
        }
        
        response = client.post('/api/v1/market/sentiment/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'analysis' in data['data']
    
    def test_analyze_sentiment_missing_content(self, client):
        """测试AI舆情分析缺少内容"""
        analyze_data = {
            'source': '新闻',
            'title': '市场动态'
        }
        
        response = client.post('/api/v1/market/sentiment/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_analyze_sentiment_empty_body(self, client):
        """测试AI舆情分析空请求体"""
        response = client.post('/api/v1/market/sentiment/analyze',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_sentiment_not_found(self, client):
        """测试获取不存在的舆情记录"""
        response = client.get('/api/v1/market/sentiment/sen_nonexistent')
        
        assert response.status_code == 404
    
    def test_update_sentiment_not_found(self, client):
        """测试更新不存在的舆情记录"""
        update_data = {'status': 'resolved'}
        
        response = client.put('/api/v1/market/sentiment/sen_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_update_sentiment_empty_body(self, client):
        """测试更新舆情记录空请求体"""
        response = client.put('/api/v1/market/sentiment/sen_001',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_sentiment_dashboard(self, client):
        """测试获取舆情监控面板"""
        response = client.get('/api/v1/market/sentiment/dashboard')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_generate_sentiment_report(self, client):
        """测试生成舆情报告"""
        report_data = {
            'start_date': '2026-04-01',
            'end_date': '2026-04-30'
        }
        
        response = client.post('/api/v1/market/sentiment/report',
                              data=json.dumps(report_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data


class TestProductEndpoints:
    """产品分析端点测试类"""
    
    def test_list_products_success(self, client):
        """测试获取产品分析列表成功"""
        response = client.get('/api/v1/market/products')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_products_with_filters(self, client):
        """测试带过滤条件获取产品分析"""
        response = client.get('/api/v1/market/products?product_type=股票型&company=XX基金')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_list_products_invalid_page(self, client):
        """测试无效页码"""
        response = client.get('/api/v1/market/products?page=0')
        
        assert response.status_code == 400
    
    def test_list_products_invalid_page_size(self, client):
        """测试无效每页条数"""
        response = client.get('/api/v1/market/products?page_size=200')
        
        assert response.status_code == 400
    
    @patch('app.routes.market.ProductService')
    def test_analyze_product_success(self, mock_product_service, client):
        """测试AI产品分析成功"""
        # Mock 产品服务
        mock_service = MagicMock()
        mock_service.analyze.return_value = {
            'analysis_content': '产品分析内容',
            'performance_data': {},
            'risk_metrics': {},
            'recommendation': '推荐意见'
        }
        mock_service.save_analysis.return_value = {'id': 'pa_001'}
        mock_product_service.return_value = mock_service
        
        analyze_data = {
            'product_name': 'XX成长基金',
            'product_type': '股票型',
            'company': 'XX基金',
            'fund_code': '000001',
            'fund_size': 1000000000
        }
        
        response = client.post('/api/v1/market/products/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_analyze_product_missing_product_name(self, client):
        """测试AI产品分析缺少产品名称"""
        analyze_data = {
            'product_type': '股票型',
            'company': 'XX基金'
        }
        
        response = client.post('/api/v1/market/products/analyze',
                              data=json.dumps(analyze_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_analyze_product_empty_body(self, client):
        """测试AI产品分析空请求体"""
        response = client.post('/api/v1/market/products/analyze',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.routes.market.ProductService')
    def test_compare_products_success(self, mock_product_service, client):
        """测试竞品对比分析成功"""
        # Mock 产品服务
        mock_service = MagicMock()
        mock_service.compare.return_value = {
            'comparison_result': '对比结果',
            'recommendations': []
        }
        mock_product_service.return_value = mock_service
        
        compare_data = {
            'products': [
                {'product_name': '产品A', 'product_type': '股票型', 'company': '公司A'},
                {'product_name': '产品B', 'product_type': '股票型', 'company': '公司B'}
            ]
        }
        
        response = client.post('/api/v1/market/products/compare',
                              data=json.dumps(compare_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
    
    def test_compare_products_insufficient_products(self, client):
        """测试竞品对比产品数量不足"""
        compare_data = {
            'products': [
                {'product_name': '产品A', 'product_type': '股票型', 'company': '公司A'}
            ]
        }
        
        response = client.post('/api/v1/market/products/compare',
                              data=json.dumps(compare_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_compare_products_too_many_products(self, client):
        """测试竞品对比产品数量过多"""
        compare_data = {
            'products': [
                {'product_name': f'产品{i}', 'product_type': '股票型', 'company': f'公司{i}'}
                for i in range(6)
            ]
        }
        
        response = client.post('/api/v1/market/products/compare',
                              data=json.dumps(compare_data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_compare_products_empty_body(self, client):
        """测试竞品对比空请求体"""
        response = client.post('/api/v1/market/products/compare',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_product_not_found(self, client):
        """测试获取不存在的产品分析"""
        response = client.get('/api/v1/market/products/pa_nonexistent')
        
        assert response.status_code == 404


class TestTrendsEndpoints:
    """市场动态端点测试类"""
    
    def test_get_trends_success(self, client):
        """测试获取市场动态成功"""
        response = client.get('/api/v1/market/trends')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'trends' in data['data']
    
    def test_get_trends_with_filters(self, client):
        """测试带过滤条件获取市场动态"""
        response = client.get('/api/v1/market/trends?category=policy&impact_level=high')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'trends' in data['data']
    
    def test_get_trends_with_max_results(self, client):
        """测试限制返回条数获取市场动态"""
        response = client.get('/api/v1/market/trends?max_results=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'trends' in data['data']
