"""
数据分析与洞察模块API路由
提供客户画像、异常识别、流失预警、报表服务等API
"""

import logging
from collections import namedtuple
from flask import Blueprint, request, current_app

from app.utils.response import (
    success_response, paginated_response, bad_request, 
    not_found, internal_error
)
from app.storage.profile_storage import CustomerProfileStorage
from app.storage.anomaly_storage import AnomalyAlertStorage
from app.storage.churn_storage import ChurnRiskStorage
from app.storage.report_storage import ReportStorage
from app.services.profile_service import ProfileService
from app.services.anomaly_service import AnomalyService
from app.services.churn_service import ChurnService
from app.services.report_service import ReportService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

# 创建蓝图
analytics_bp = Blueprint('analytics', __name__)

# 定义命名元组类型
Services = namedtuple('Services', [
    'llm_service', 'profile_service', 'anomaly_service', 'churn_service', 'report_service',
    'profile_storage', 'anomaly_storage', 'churn_storage', 'report_storage'
])


def _get_services():
    """
    获取服务实例
    
    Returns:
        Services: 包含所有服务和存储实例的命名元组
    """
    data_dir = current_app.config.get('DATA_DIR', './data')
    
    # 初始化LLM服务
    llm_config = {
        'LLM_API_KEY': current_app.config.get('LLM_API_KEY', ''),
        'LLM_API_URL': current_app.config.get('LLM_API_URL', ''),
        'LLM_MODEL': current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_TIMEOUT': current_app.config.get('LLM_TIMEOUT', 30)
    }
    llm_service = LLMService(llm_config)
    
    # 初始化存储层
    profile_storage = CustomerProfileStorage(data_dir)
    anomaly_storage = AnomalyAlertStorage(data_dir)
    churn_storage = ChurnRiskStorage(data_dir)
    report_storage = ReportStorage(data_dir)
    
    # 初始化服务层
    profile_service = ProfileService(llm_service, profile_storage)
    anomaly_service = AnomalyService(llm_service, anomaly_storage)
    churn_service = ChurnService(llm_service, churn_storage, profile_storage)
    report_service = ReportService(
        llm_service, report_storage,
        profile_storage, anomaly_storage, churn_storage
    )
    
    return Services(
        llm_service=llm_service,
        profile_service=profile_service,
        anomaly_service=anomaly_service,
        churn_service=churn_service,
        report_service=report_service,
        profile_storage=profile_storage,
        anomaly_storage=anomaly_storage,
        churn_storage=churn_storage,
        report_storage=report_storage
    )


# ==================== 客户画像API ====================

@analytics_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """
    获取客户画像列表
    
    Query参数:
    - page: 页码（默认1）
    - page_size: 每页条数（默认20）
    - value_tier: 价值分层筛选（high/medium/low）
    - tag: 标签筛选
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        value_tier = request.args.get('value_tier')
        tag = request.args.get('tag')
        
        s = _get_services()
        profile_storage = s.profile_storage
        
        # 构建过滤条件
        filters = {}
        if value_tier:
            filters['value_tier'] = value_tier
        
        # 如果有标签筛选，使用特殊查询
        if tag:
            items = profile_storage.find_by_tags([tag])
            total = len(items)
            # 手动分页
            start = (page - 1) * page_size
            end = start + page_size
            paginated_items = items[start:end]
            return paginated_response(
                items=paginated_items,
                total=total,
                page=page,
                page_size=page_size
            )
        
        result = profile_storage.list(
            filters=filters if filters else None,
            page=page,
            page_size=page_size,
            sort_by='updated_at',
            sort_order='desc'
        )
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
        
    except Exception as e:
        logger.error(f"获取客户画像列表失败: {e}")
        return internal_error(message="获取客户画像列表失败")


@analytics_bp.route('/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """
    获取客户画像详情
    
    Path参数:
    - profile_id: 客户画像ID
    """
    try:
        s = _get_services()
        profile_storage = s.profile_storage
        
        profile = profile_storage.get(profile_id)
        if not profile:
            return not_found(message="客户画像不存在")
        
        return success_response(data=profile)
        
    except Exception as e:
        logger.error(f"获取客户画像详情失败: {e}")
        return internal_error(message="获取客户画像详情失败")


@analytics_bp.route('/profiles/analyze', methods=['POST'])
def analyze_profile():
    """
    AI分析客户画像
    
    Request Body:
    - customer_data: 客户数据
    - save: 是否保存分析结果（默认false）
    """
    try:
        data = request.get_json()
        if not data or 'customer_data' not in data:
            return bad_request(message="缺少customer_data参数")
        
        customer_data = data['customer_data']
        save = data.get('save', False)
        
        s = _get_services()
        profile_service = s.profile_service
        profile_storage = s.profile_storage
        
        # 执行AI分析
        analysis = profile_service.analyze_profile(customer_data)
        
        result = {
            'analysis': analysis,
            'saved': False
        }
        
        # 如果需要保存
        if save:
            # 合并客户数据和分析结果
            profile_data = {**customer_data, **analysis}
            created = profile_service.create_profile(profile_data, auto_analyze=False)
            result['profile'] = created
            result['saved'] = True
        
        return success_response(data=result, message="分析完成")
        
    except Exception as e:
        logger.error(f"AI分析客户画像失败: {e}")
        return internal_error(message="AI分析失败")


@analytics_bp.route('/profiles/<profile_id>/similar', methods=['GET'])
def get_similar_profiles(profile_id):
    """
    获取相似客户
    
    Path参数:
    - profile_id: 参考客户画像ID
    
    Query参数:
    - top_n: 返回数量（默认5）
    """
    try:
        top_n = request.args.get('top_n', 5, type=int)
        
        s = _get_services()
        
        similar = s.profile_service.find_similar(profile_id, top_n)
        
        return success_response(data={
            'profile_id': profile_id,
            'similar_customers': similar,
            'count': len(similar)
        })
        
    except Exception as e:
        logger.error(f"查找相似客户失败: {e}")
        return internal_error(message="查找相似客户失败")


@analytics_bp.route('/profiles/<profile_id>/insights', methods=['GET'])
def get_profile_insights(profile_id):
    """
    获取客户洞察
    
    Path参数:
    - profile_id: 客户画像ID
    """
    try:
        s = _get_services()
        
        insights = s.profile_service.get_insights(profile_id)
        
        if 'error' in insights:
            return not_found(message=insights['error'])
        
        return success_response(data=insights)
        
    except Exception as e:
        logger.error(f"获取客户洞察失败: {e}")
        return internal_error(message="获取客户洞察失败")


@analytics_bp.route('/profiles/tags', methods=['GET'])
def get_profile_tags():
    """
    获取标签体系
    
    返回所有可用的客户标签及统计
    """
    try:
        s = _get_services()
        profile_storage = s.profile_storage
        
        stats = profile_storage.get_tag_statistics()
        
        return success_response(data={
            'tags': stats.get('tag_distribution', {}),
            'tier_distribution': stats.get('tier_distribution', {}),
            'risk_distribution': stats.get('risk_distribution', {}),
            'total_profiles': stats.get('total_profiles', 0)
        })
        
    except Exception as e:
        logger.error(f"获取标签体系失败: {e}")
        return internal_error(message="获取标签体系失败")


# ==================== 异常识别API ====================

@analytics_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """
    获取异常告警列表
    
    Query参数:
    - page: 页码（默认1）
    - page_size: 每页条数（默认20）
    - severity: 严重程度筛选（critical/high/medium/low）
    - status: 状态筛选（new/investigating/resolved/dismissed）
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        severity = request.args.get('severity')
        status = request.args.get('status')
        
        s = _get_services()
        anomaly_storage = s.anomaly_storage
        
        # 构建过滤条件
        filters = {}
        if severity:
            filters['severity'] = severity
        if status:
            filters['status'] = status
        
        result = anomaly_storage.list(
            filters=filters if filters else None,
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
        
    except Exception as e:
        logger.error(f"获取异常告警列表失败: {e}")
        return internal_error(message="获取异常告警列表失败")


@analytics_bp.route('/anomalies/<alert_id>', methods=['GET'])
def get_anomaly(alert_id):
    """
    获取异常告警详情
    
    Path参数:
    - alert_id: 告警ID
    """
    try:
        s = _get_services()
        anomaly_storage = s.anomaly_storage
        
        alert = anomaly_storage.get(alert_id)
        if not alert:
            return not_found(message="告警不存在")
        
        return success_response(data=alert)
        
    except Exception as e:
        logger.error(f"获取告警详情失败: {e}")
        return internal_error(message="获取告警详情失败")


@analytics_bp.route('/anomalies/detect', methods=['POST'])
def detect_anomaly():
    """
    异常检测
    
    Request Body:
    - customer_id: 客户ID
    - customer_name: 客户姓名
    - transaction_data: 交易数据
    - create_alert: 是否创建告警（默认true）
    """
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name', '未知客户')
        transaction_data = data.get('transaction_data')
        create_alert = data.get('create_alert', True)
        
        if not transaction_data:
            return bad_request(message="缺少transaction_data参数")
        
        s = _get_services()
        anomaly_service = s.anomaly_service
        
        if create_alert and customer_id:
            result = s.anomaly_service.create_alert(
                customer_id=customer_id,
                customer_name=customer_name,
                transaction_data=transaction_data
            )
        else:
            result = anomaly_service.detect(transaction_data)
        
        return success_response(data=result, message="检测完成")
        
    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        return internal_error(message="异常检测失败")


@analytics_bp.route('/anomalies/<alert_id>/analyze', methods=['POST'])
def analyze_anomaly(alert_id):
    """
    AI分析异常
    
    Path参数:
    - alert_id: 告警ID
    """
    try:
        s = _get_services()
        
        analysis = s.anomaly_service.analyze(alert_id)
        
        if 'error' in analysis:
            return not_found(message=analysis['error'])
        
        return success_response(data=analysis, message="分析完成")
        
    except Exception as e:
        logger.error(f"异常分析失败: {e}")
        return internal_error(message="异常分析失败")


@analytics_bp.route('/anomalies/<alert_id>', methods=['PUT'])
def update_anomaly_status(alert_id):
    """
    更新告警状态
    
    Path参数:
    - alert_id: 告警ID
    
    Request Body:
    - status: 新状态（new/investigating/resolved/dismissed）
    - analysis: 分析结果（可选）
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return bad_request(message="缺少status参数")
        
        status = data['status']
        analysis = data.get('analysis')
        
        s = _get_services()
        anomaly_storage = s.anomaly_storage
        
        updated = anomaly_storage.update_status(alert_id, status, analysis)
        
        if not updated:
            return not_found(message="告警不存在")
        
        return success_response(data=updated, message="状态更新成功")
        
    except Exception as e:
        logger.error(f"更新告警状态失败: {e}")
        return internal_error(message="更新告警状态失败")


@analytics_bp.route('/anomalies/statistics', methods=['GET'])
def get_anomaly_statistics():
    """
    获取异常统计
    """
    try:
        s = _get_services()
        anomaly_storage = s.anomaly_storage
        
        stats = anomaly_storage.get_statistics()
        
        return success_response(data=stats)
        
    except Exception as e:
        logger.error(f"获取异常统计失败: {e}")
        return internal_error(message="获取异常统计失败")


# ==================== 流失预警API ====================

@analytics_bp.route('/churn/risks', methods=['GET'])
def get_churn_risks():
    """
    获取流失预警列表
    
    Query参数:
    - page: 页码（默认1）
    - page_size: 每页条数（默认20）
    - risk_level: 风险等级筛选（critical/high/medium/low）
    - status: 状态筛选（new/contacted/retained/churned）
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        risk_level = request.args.get('risk_level')
        status = request.args.get('status')
        
        s = _get_services()
        churn_storage = s.churn_storage
        
        # 构建过滤条件
        filters = {}
        if risk_level:
            filters['risk_level'] = risk_level
        if status:
            filters['status'] = status
        
        result = churn_storage.list(
            filters=filters if filters else None,
            page=page,
            page_size=page_size,
            sort_by='risk_score',
            sort_order='desc'
        )
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
        
    except Exception as e:
        logger.error(f"获取流失预警列表失败: {e}")
        return internal_error(message="获取流失预警列表失败")


@analytics_bp.route('/churn/predict', methods=['POST'])
def predict_churn():
    """
    流失预测
    
    Request Body:
    - customer_id: 客户ID
    - customer_name: 客户姓名
    - customer_data: 客户数据
    - create_record: 是否创建风险记录（默认true）
    """
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name', '未知客户')
        customer_data = data.get('customer_data', {})
        create_record = data.get('create_record', True)
        
        s = _get_services()
        
        # 执行预测
        prediction = s.churn_service.predict(customer_data)
        
        result = {
            'prediction': prediction,
            'record_created': False
        }
        
        # 创建风险记录
        if create_record and customer_id:
            record = s.churn_service.create_risk_record(
                customer_id=customer_id,
                customer_name=customer_name,
                customer_data=customer_data
            )
            result['record'] = record
            result['record_created'] = True
        
        return success_response(data=result, message="预测完成")
        
    except Exception as e:
        logger.error(f"流失预测失败: {e}")
        return internal_error(message="流失预测失败")


@analytics_bp.route('/churn/risks/<risk_id>/retention', methods=['POST'])
def generate_retention_plan(risk_id):
    """
    生成挽留建议
    
    Path参数:
    - risk_id: 风险记录ID
    """
    try:
        s = _get_services()
        churn_service = s.churn_service
        
        # 获取风险记录
        s = _get_services()
        churn_storage = s.churn_storage
        risk_record = churn_storage.get(risk_id)
        
        if not risk_record:
            return not_found(message="风险记录不存在")
        
        plan = churn_service.generate_retention_plan(risk_record['customer_id'])
        
        if 'error' in plan:
            return bad_request(message=plan['error'])
        
        return success_response(data=plan, message="挽留建议生成完成")
        
    except Exception as e:
        logger.error(f"生成挽留建议失败: {e}")
        return internal_error(message="生成挽留建议失败")


@analytics_bp.route('/churn/risks/<risk_id>', methods=['PUT'])
def update_churn_status(risk_id):
    """
    更新流失风险状态
    
    Path参数:
    - risk_id: 风险记录ID
    
    Request Body:
    - status: 新状态（new/contacted/retained/churned）
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return bad_request(message="缺少status参数")
        
        status = data['status']
        
        s = _get_services()
        churn_storage = s.churn_storage
        
        updated = churn_storage.update_status(risk_id, status)
        
        if not updated:
            return not_found(message="风险记录不存在")
        
        return success_response(data=updated, message="状态更新成功")
        
    except Exception as e:
        logger.error(f"更新流失风险状态失败: {e}")
        return internal_error(message="更新流失风险状态失败")


@analytics_bp.route('/churn/statistics', methods=['GET'])
def get_churn_statistics():
    """
    获取流失预警统计
    """
    try:
        s = _get_services()
        
        summary = s.churn_service.get_high_risk_summary()
        
        return success_response(data=summary)
        
    except Exception as e:
        logger.error(f"获取流失统计失败: {e}")
        return internal_error(message="获取流失统计失败")


# ==================== 报表服务API ====================

@analytics_bp.route('/reports', methods=['GET'])
def get_reports():
    """
    获取报表列表
    
    Query参数:
    - page: 页码（默认1）
    - page_size: 每页条数（默认20）
    - type: 类型筛选（daily/weekly/monthly/custom）
    - category: 类别筛选（service/complaint/quality/customer）
    - status: 状态筛选（draft/generating/completed/failed）
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        report_type = request.args.get('type')
        category = request.args.get('category')
        status = request.args.get('status')
        
        s = _get_services()
        report_storage = s.report_storage
        
        # 构建过滤条件
        filters = {}
        if report_type:
            filters['type'] = report_type
        if category:
            filters['category'] = category
        if status:
            filters['status'] = status
        
        result = report_storage.list(
            filters=filters if filters else None,
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
        
    except Exception as e:
        logger.error(f"获取报表列表失败: {e}")
        return internal_error(message="获取报表列表失败")


@analytics_bp.route('/reports/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    获取报表详情
    
    Path参数:
    - report_id: 报表ID
    """
    try:
        s = _get_services()
        report_storage = s.report_storage
        
        report = report_storage.get(report_id)
        if not report:
            return not_found(message="报表不存在")
        
        return success_response(data=report)
        
    except Exception as e:
        logger.error(f"获取报表详情失败: {e}")
        return internal_error(message="获取报表详情失败")


@analytics_bp.route('/reports', methods=['POST'])
def create_report():
    """
    创建报表
    
    Request Body:
    - title: 报表标题
    - type: 报表类型（daily/weekly/monthly/custom）
    - category: 报表类别（service/complaint/quality/customer）
    - parameters: 报表参数
    """
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        title = data.get('title')
        report_type = data.get('type')
        category = data.get('category', 'service')
        parameters = data.get('parameters', {})
        
        if not title or not report_type:
            return bad_request(message="缺少title或type参数")
        
        s = _get_services()
        report_storage = s.report_storage
        
        report = report_storage.create_report(
            title=title,
            report_type=report_type,
            category=category,
            parameters=parameters,
            created_by='user'  # TODO: 从认证信息获取
        )
        
        return success_response(data=report, message="报表创建成功", code=201)
        
    except Exception as e:
        logger.error(f"创建报表失败: {e}")
        return internal_error(message="创建报表失败")


@analytics_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """
    AI生成报表
    
    Request Body:
    - type: 报表类型（daily/weekly/monthly/custom）
    - category: 报表类别（service/complaint/quality/customer）
    - parameters: 报表参数
    """
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        report_type = data.get('type')
        category = data.get('category', 'service')
        parameters = data.get('parameters', {})
        
        if not report_type:
            return bad_request(message="缺少type参数")
        
        s = _get_services()
        
        # 根据类型调用不同的生成方法
        if report_type == 'daily':
            report = s.report_service.generate_daily_report(
                parameters.get('date')
            )
        elif report_type == 'weekly':
            report = s.report_service.generate_weekly_report(
                parameters.get('week_start')
            )
        elif report_type == 'monthly':
            report = s.report_service.generate_monthly_report(
                parameters.get('year'),
                parameters.get('month')
            )
        else:
            report = s.report_service.generate(
                report_type=report_type,
                parameters=parameters
            )
        
        if 'error' in report:
            return internal_error(message=report['error'])
        
        return success_response(data=report, message="报表生成完成")
        
    except Exception as e:
        logger.error(f"生成报表失败: {e}")
        return internal_error(message="生成报表失败")


@analytics_bp.route('/reports/<report_id>/summary', methods=['GET'])
def get_report_summary(report_id):
    """
    获取报表AI摘要
    
    Path参数:
    - report_id: 报表ID
    """
    try:
        s = _get_services()
        
        summary = s.report_service.get_summary(report_id)
        
        if 'error' in summary:
            return not_found(message=summary['error'])
        
        return success_response(data=summary)
        
    except Exception as e:
        logger.error(f"获取报表摘要失败: {e}")
        return internal_error(message="获取报表摘要失败")


@analytics_bp.route('/reports/statistics', methods=['GET'])
def get_report_statistics():
    """
    获取报表统计
    """
    try:
        s = _get_services()
        report_storage = s.report_storage
        
        stats = report_storage.get_statistics()
        
        return success_response(data=stats)
        
    except Exception as e:
        logger.error(f"获取报表统计失败: {e}")
        return internal_error(message="获取报表统计失败")
