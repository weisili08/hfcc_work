"""
市场监测API路由
提供舆情监控、产品分析和市场动态功能
"""

from flask import Blueprint, request, current_app

from app.utils.response import success_response, paginated_response, bad_request, not_found
from app.services.llm_service import LLMService
from app.services.sentiment_service import SentimentService
from app.services.product_service import ProductService
from app.storage.sentiment_storage import SentimentRecordStorage
from app.storage.product_storage import ProductAnalysisStorage

# 创建蓝图
market_bp = Blueprint('market', __name__)


def _get_sentiment_service():
    """获取舆情服务实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    llm_service = LLMService(current_app.config)
    storage = SentimentRecordStorage(data_dir)
    return SentimentService(llm_service, storage)


def _get_product_service():
    """获取产品服务实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    llm_service = LLMService(current_app.config)
    storage = ProductAnalysisStorage(data_dir)
    return ProductService(llm_service, storage)


# ==================== 舆情相关接口 ====================

@market_bp.route('/sentiment', methods=['GET'])
def list_sentiment():
    """
    舆情列表
    
    Query参数:
        - sentiment: 情感筛选 (positive/neutral/negative)
        - severity: 严重程度筛选 (critical/high/medium/low)
        - status: 状态筛选 (new/monitoring/resolved/archived)
        - source: 来源筛选
        - page: 页码，默认1
        - page_size: 每页条数，默认20
    
    Returns:
        分页舆情列表
    """
    try:
        # 获取查询参数
        sentiment = request.args.get('sentiment')
        severity = request.args.get('severity')
        status = request.args.get('status')
        source = request.args.get('source')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 参数校验
        if page < 1:
            return bad_request(message='页码必须大于0')
        if page_size < 1 or page_size > 100:
            return bad_request(message='每页条数必须在1-100之间')
        
        # 构建过滤条件
        filters = {}
        if sentiment:
            filters['sentiment'] = sentiment
        if severity:
            filters['severity'] = severity
        if status:
            filters['status'] = status
        if source:
            filters['source'] = source
        
        service = _get_sentiment_service()
        result = service.list_records(filters=filters, page=page, page_size=page_size)
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
    
    except Exception as e:
        current_app.logger.error(f"List sentiment records failed: {str(e)}")
        return success_response(data={'items': [], 'total': 0})


@market_bp.route('/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """
    AI舆情分析
    
    Request Body:
        - content: 舆情内容 (必填)
        - source: 来源
        - title: 标题
    
    Returns:
        分析结果
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        content = data.get('content')
        if not content:
            return bad_request(message='缺少必填字段: content')
        
        source = data.get('source')
        
        service = _get_sentiment_service()
        analysis = service.analyze(content, source)
        
        # 保存分析记录
        record_data = {
            'title': data.get('title', content[:50] + '...'),
            'source': source or 'manual',
            'content': content,
            'sentiment': analysis.get('sentiment'),
            'severity': analysis.get('severity'),
            'keywords': analysis.get('keywords', []),
            'related_products': analysis.get('related_products', []),
            'status': 'new',
            'alert_level': analysis.get('alert_level'),
            'analysis': analysis
        }
        
        saved_record = service.save_record(record_data)
        
        return success_response(data={
            'analysis': analysis,
            'record': saved_record
        }, message='分析完成')
    
    except Exception as e:
        current_app.logger.error(f"Sentiment analysis failed: {str(e)}")
        return success_response(data={'error': str(e)})


@market_bp.route('/sentiment/<record_id>', methods=['GET'])
def get_sentiment(record_id):
    """
    获取舆情详情
    
    Args:
        record_id: 舆情ID
    
    Returns:
        舆情详情
    """
    try:
        service = _get_sentiment_service()
        record = service.get_record(record_id)
        
        if not record:
            return not_found(message='舆情记录不存在')
        
        return success_response(data=record)
    
    except Exception as e:
        current_app.logger.error(f"Get sentiment record failed: {str(e)}")
        return not_found(message='舆情记录不存在')


@market_bp.route('/sentiment/<record_id>', methods=['PUT'])
def update_sentiment(record_id):
    """
    更新舆情状态
    
    Args:
        record_id: 舆情ID
    
    Request Body:
        - status: 新状态 (new/monitoring/resolved/archived)
        - 其他要更新的字段
    
    Returns:
        更新后的记录
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        service = _get_sentiment_service()
        
        # 检查记录是否存在
        existing = service.get_record(record_id)
        if not existing:
            return not_found(message='舆情记录不存在')
        
        # 更新字段
        updates = {k: v for k, v in data.items() if k not in ['id', 'created_at']}
        result = service.storage.update_record(record_id, updates)
        
        return success_response(data=result, message='更新成功')
    
    except Exception as e:
        current_app.logger.error(f"Update sentiment record failed: {str(e)}")
        return success_response(data={'error': str(e)})


@market_bp.route('/sentiment/dashboard', methods=['GET'])
def get_sentiment_dashboard():
    """
    舆情监控面板
    
    Returns:
        面板数据（趋势、分布、预警）
    """
    try:
        service = _get_sentiment_service()
        dashboard = service.get_dashboard()
        
        return success_response(data=dashboard)
    
    except Exception as e:
        current_app.logger.error(f"Get sentiment dashboard failed: {str(e)}")
        return success_response(data={
            'overview': {'total_records': 0, 'alert_count': 0, 'new_today': 0, 'new_this_week': 0},
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
            'severity_distribution': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'source_distribution': {},
            'trend': [],
            'latest_alerts': [],
            'latest_records': []
        })


@market_bp.route('/sentiment/report', methods=['POST'])
def generate_sentiment_report():
    """
    生成舆情报告
    
    Request Body:
        - start_date: 开始日期
        - end_date: 结束日期
    
    Returns:
        报告数据
    """
    try:
        data = request.get_json() or {}
        
        date_range = None
        if 'start_date' in data and 'end_date' in data:
            date_range = {
                'start_date': data['start_date'],
                'end_date': data['end_date']
            }
        
        service = _get_sentiment_service()
        report = service.generate_report(date_range)
        
        return success_response(data=report, message='报告生成成功')
    
    except Exception as e:
        current_app.logger.error(f"Generate sentiment report failed: {str(e)}")
        return success_response(data={'error': str(e)})


# ==================== 产品分析相关接口 ====================

@market_bp.route('/products', methods=['GET'])
def list_products():
    """
    产品分析列表
    
    Query参数:
        - product_type: 产品类型筛选
        - company: 基金公司筛选
        - status: 状态筛选 (draft/published)
        - page: 页码，默认1
        - page_size: 每页条数，默认20
    
    Returns:
        分页产品分析列表
    """
    try:
        # 获取查询参数
        product_type = request.args.get('product_type')
        company = request.args.get('company')
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 参数校验
        if page < 1:
            return bad_request(message='页码必须大于0')
        if page_size < 1 or page_size > 100:
            return bad_request(message='每页条数必须在1-100之间')
        
        # 构建过滤条件
        filters = {}
        if product_type:
            filters['product_type'] = product_type
        if company:
            filters['company'] = company
        if status:
            filters['status'] = status
        
        service = _get_product_service()
        result = service.list_analyses(filters=filters, page=page, page_size=page_size)
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
    
    except Exception as e:
        current_app.logger.error(f"List product analyses failed: {str(e)}")
        return success_response(data={'items': [], 'total': 0})


@market_bp.route('/products/analyze', methods=['POST'])
def analyze_product():
    """
    AI产品分析
    
    Request Body:
        - product_name: 产品名称 (必填)
        - product_type: 产品类型
        - company: 基金公司
        - fund_code: 基金代码
        - establishment_date: 成立日期
        - fund_size: 基金规模
        - investment_strategy: 投资策略
    
    Returns:
        分析结果
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        product_name = data.get('product_name')
        if not product_name:
            return bad_request(message='缺少必填字段: product_name')
        
        product_info = {
            'product_name': product_name,
            'product_type': data.get('product_type', '未知'),
            'company': data.get('company', '未知'),
            'fund_code': data.get('fund_code'),
            'establishment_date': data.get('establishment_date'),
            'fund_size': data.get('fund_size'),
            'investment_strategy': data.get('investment_strategy')
        }
        
        service = _get_product_service()
        analysis = service.analyze(product_info)
        
        # 保存分析结果
        analysis_data = {
            'product_name': product_name,
            'product_type': product_info['product_type'],
            'company': product_info['company'],
            'analysis_content': analysis.get('analysis_content'),
            'performance_data': analysis.get('performance_data'),
            'risk_metrics': analysis.get('risk_metrics'),
            'recommendation': analysis.get('recommendation'),
            'status': 'published'
        }
        
        created_by = data.get('created_by', 'system')
        saved_analysis = service.save_analysis(analysis_data, created_by)
        
        return success_response(data={
            'analysis': analysis,
            'record': saved_analysis
        }, message='分析完成')
    
    except Exception as e:
        current_app.logger.error(f"Product analysis failed: {str(e)}")
        return success_response(data={'error': str(e)})


@market_bp.route('/products/compare', methods=['POST'])
def compare_products():
    """
    竞品对比分析
    
    Request Body:
        - products: 产品列表 (必填，至少2个)
            [
                {
                    "product_name": "产品名称",
                    "product_type": "产品类型",
                    "company": "基金公司"
                }
            ]
    
    Returns:
        对比分析结果
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        products = data.get('products')
        if not products or len(products) < 2:
            return bad_request(message='至少需要2个产品进行对比')
        
        if len(products) > 5:
            return bad_request(message='最多支持5个产品对比')
        
        service = _get_product_service()
        comparison = service.compare(products)
        
        return success_response(data=comparison, message='对比分析完成')
    
    except Exception as e:
        current_app.logger.error(f"Product comparison failed: {str(e)}")
        return success_response(data={'error': str(e)})


@market_bp.route('/products/<analysis_id>', methods=['GET'])
def get_product(analysis_id):
    """
    获取产品分析详情
    
    Args:
        analysis_id: 分析ID
    
    Returns:
        产品分析详情
    """
    try:
        service = _get_product_service()
        analysis = service.get_analysis(analysis_id)
        
        if not analysis:
            return not_found(message='产品分析不存在')
        
        return success_response(data=analysis)
    
    except Exception as e:
        current_app.logger.error(f"Get product analysis failed: {str(e)}")
        return not_found(message='产品分析不存在')


# ==================== 市场动态接口 ====================

@market_bp.route('/trends', methods=['GET'])
def get_trends():
    """
    市场动态
    
    Query参数:
        - category: 类别筛选 (policy/market/industry/fund)
        - impact_level: 影响程度筛选 (high/medium/low)
        - max_results: 最大条数，默认20
    
    Returns:
        市场动态列表
    """
    try:
        category = request.args.get('category')
        impact_level = request.args.get('impact_level')
        max_results = request.args.get('max_results', 20, type=int)
        
        # 模拟市场动态数据
        trends = [
            {
                'trend_id': 'trend_001',
                'category': 'policy',
                'title': '证监会发布新的基金销售管理办法',
                'description': '新规对基金销售机构的适当性管理提出了更高要求',
                'impact_level': 'high',
                'occurred_at': '2026-04-15T10:00:00Z',
                'related_products': ['所有基金产品'],
                'impact_analysis': '将提升行业合规水平，保护投资者权益',
                'suggested_response': '及时学习新规，调整销售流程'
            },
            {
                'trend_id': 'trend_002',
                'category': 'market',
                'title': 'A股市场震荡调整',
                'description': '近期A股市场出现一定幅度调整，投资者情绪趋于谨慎',
                'impact_level': 'medium',
                'occurred_at': '2026-04-14T14:30:00Z',
                'related_products': ['股票型基金', '混合型基金'],
                'impact_analysis': '短期可能影响权益类产品净值',
                'suggested_response': '加强投资者沟通，做好风险提示'
            },
            {
                'trend_id': 'trend_003',
                'category': 'industry',
                'title': '公募基金规模突破30万亿',
                'description': '行业整体规模持续增长，显示投资者信心增强',
                'impact_level': 'medium',
                'occurred_at': '2026-04-13T09:00:00Z',
                'related_products': ['所有基金产品'],
                'impact_analysis': '行业向好，有利于品牌宣传',
                'suggested_response': '把握机遇，加强产品推广'
            }
        ]
        
        # 应用过滤
        if category:
            trends = [t for t in trends if t['category'] == category]
        if impact_level:
            trends = [t for t in trends if t['impact_level'] == impact_level]
        
        # 限制条数
        trends = trends[:max_results]
        
        return success_response(data={
            'briefing_date': '2026-04-15',
            'summary': '今日市场动态：政策层面有新规定发布，市场层面A股震荡调整，行业层面规模持续增长。',
            'trends': trends
        })
    
    except Exception as e:
        current_app.logger.error(f"Get market trends failed: {str(e)}")
        return success_response(data={'trends': []})
