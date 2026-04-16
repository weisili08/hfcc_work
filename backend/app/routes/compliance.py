"""
合规检查API路由
提供合规检查、风险提示和反洗钱检查功能
"""

from flask import Blueprint, request, current_app

from app.utils.response import success_response, paginated_response, bad_request, not_found
from app.services.llm_service import LLMService
from app.services.compliance_service import ComplianceService
from app.storage.compliance_storage import ComplianceCheckStorage

# 创建蓝图
compliance_bp = Blueprint('compliance', __name__)


def _get_compliance_service():
    """获取合规服务实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    llm_service = LLMService(current_app.config)
    storage = ComplianceCheckStorage(data_dir)
    return ComplianceService(llm_service, storage)


@compliance_bp.route('/checks', methods=['GET'])
def list_checks():
    """
    检查记录列表
    
    Query参数:
        - check_type: 检查类型筛选 (content/process/transaction/communication)
        - result: 结果筛选 (pass/warning/violation)
        - risk_level: 风险等级筛选 (low/medium/high/critical)
        - page: 页码，默认1
        - page_size: 每页条数，默认20
    
    Returns:
        分页检查记录列表
    """
    try:
        # 获取查询参数
        check_type = request.args.get('check_type')
        result = request.args.get('result')
        risk_level = request.args.get('risk_level')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 参数校验
        if page < 1:
            return bad_request(message='页码必须大于0')
        if page_size < 1 or page_size > 100:
            return bad_request(message='每页条数必须在1-100之间')
        
        # 构建过滤条件
        filters = {}
        if check_type:
            filters['check_type'] = check_type
        if result:
            filters['result'] = result
        if risk_level:
            filters['risk_level'] = risk_level
        
        service = _get_compliance_service()
        result_data = service.storage.list_checks(filters=filters, page=page, page_size=page_size)
        
        return paginated_response(
            items=result_data['items'],
            total=result_data['total'],
            page=result_data['page'],
            page_size=result_data['page_size']
        )
    
    except Exception as e:
        current_app.logger.error(f"List compliance checks failed: {str(e)}")
        return success_response(data={'items': [], 'total': 0})


@compliance_bp.route('/check', methods=['POST'])
def check_content():
    """
    AI合规检查
    
    Request Body:
        - content: 待检查内容 (必填)
        - check_type: 检查类型，默认content (content/process/transaction/communication)
    
    Returns:
        检查结果
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        content = data.get('content')
        if not content:
            return bad_request(message='缺少必填字段: content')
        
        check_type = data.get('check_type', 'content')
        
        # 校验检查类型
        valid_types = ['content', 'process', 'transaction', 'communication']
        if check_type not in valid_types:
            return bad_request(message=f'无效的check_type，必须是: {", ".join(valid_types)}')
        
        service = _get_compliance_service()
        result = service.check_content(content, check_type)
        
        return success_response(data=result, message='检查完成')
    
    except Exception as e:
        current_app.logger.error(f"Compliance check failed: {str(e)}")
        return success_response(data={'error': str(e)})


@compliance_bp.route('/checks/<check_id>', methods=['GET'])
def get_check(check_id):
    """
    获取检查详情
    
    Args:
        check_id: 检查ID
    
    Returns:
        检查详情
    """
    try:
        service = _get_compliance_service()
        check = service.storage.get_check_by_id(check_id)
        
        if not check:
            return not_found(message='检查记录不存在')
        
        return success_response(data=check)
    
    except Exception as e:
        current_app.logger.error(f"Get compliance check failed: {str(e)}")
        return not_found(message='检查记录不存在')


@compliance_bp.route('/aml/check', methods=['POST'])
def check_aml():
    """
    反洗钱检查
    
    Request Body:
        - customer_id: 客户ID
        - transaction_amount: 交易金额 (必填)
        - transaction_type: 交易类型
        - counterparty: 交易对手
        - frequency: 交易频率
    
    Returns:
        检查结果
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        # 必填字段校验
        transaction_amount = data.get('transaction_amount')
        if transaction_amount is None:
            return bad_request(message='缺少必填字段: transaction_amount')
        
        transaction_data = {
            'customer_id': data.get('customer_id'),
            'transaction_amount': transaction_amount,
            'transaction_type': data.get('transaction_type', '普通交易'),
            'counterparty': data.get('counterparty', ''),
            'frequency': data.get('frequency', '正常')
        }
        
        service = _get_compliance_service()
        result = service.check_aml(transaction_data)
        
        return success_response(data=result, message='检查完成')
    
    except Exception as e:
        current_app.logger.error(f"AML check failed: {str(e)}")
        return success_response(data={'error': str(e)})


@compliance_bp.route('/risk-tips', methods=['GET'])
def get_risk_tips():
    """
    合规风险提示列表
    
    Query参数:
        - scenario: 场景筛选 (产品销售/收益说明/风险提示/客户沟通/投诉处理)
        - risk_type: 风险类型筛选
    
    Returns:
        风险提示列表
    """
    try:
        scenario = request.args.get('scenario')
        risk_type = request.args.get('risk_type')
        
        service = _get_compliance_service()
        tips = service.get_risk_tips(scenario=scenario, risk_type=risk_type)
        
        return success_response(data={'tips': tips})
    
    except Exception as e:
        current_app.logger.error(f"Get risk tips failed: {str(e)}")
        return success_response(data={'tips': []})


@compliance_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    合规统计
    
    Returns:
        合规检查统计数据
    """
    try:
        service = _get_compliance_service()
        stats = service.get_statistics()
        
        return success_response(data=stats)
    
    except Exception as e:
        current_app.logger.error(f"Get compliance statistics failed: {str(e)}")
        return success_response(data={
            'total': 0,
            'by_result': {'pass': 0, 'warning': 0, 'violation': 0},
            'by_risk_level': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'by_type': {},
            'pass_rate': 0
        })


@compliance_bp.route('/rules', methods=['GET'])
def get_rules():
    """
    获取合规规则列表
    
    Returns:
        合规规则列表
    """
    try:
        service = _get_compliance_service()
        rules = service.RISK_RULES
        
        return success_response(data={'rules': rules})
    
    except Exception as e:
        current_app.logger.error(f"Get compliance rules failed: {str(e)}")
        return success_response(data={'rules': []})
