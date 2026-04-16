"""
质检管理API路由模块
提供质检相关的RESTful API接口
"""

from flask import Blueprint, request, current_app

from app.services.quality_service import QualityService
from app.storage.quality_storage import QualityCheckStorage
from app.services.llm_service import LLMService
from app.utils.response import (
    success_response, paginated_response,
    bad_request, not_found, internal_error
)

quality_bp = Blueprint('quality', __name__)


def get_quality_service():
    """获取质检服务实例"""
    config = {
        'LLM_API_KEY': current_app.config.get('LLM_API_KEY', ''),
        'LLM_API_URL': current_app.config.get('LLM_API_URL', ''),
        'LLM_MODEL': current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_TIMEOUT': current_app.config.get('LLM_TIMEOUT', 30)
    }
    llm_service = LLMService(config)
    data_dir = current_app.config.get('DATA_DIR', './data')
    storage = QualityCheckStorage(data_dir)
    return QualityService(llm_service, storage)


def get_quality_storage():
    """获取质检存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return QualityCheckStorage(data_dir)


@quality_bp.route('/checks', methods=['GET'])
def list_checks():
    """获取质检记录列表"""
    try:
        # 获取查询参数
        status = request.args.get('status')
        agent_name = request.args.get('agent_name')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤条件
        filters = {}
        if status:
            filters['status'] = status
        if agent_name:
            filters['agent_name'] = agent_name
        
        # 限制分页大小
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        
        storage = get_quality_storage()
        result = storage.list(
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
        current_app.logger.error(f"List quality checks error: {str(e)}")
        return internal_error(message="获取质检记录列表失败")


@quality_bp.route('/checks', methods=['POST'])
def create_check():
    """创建质检记录"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        required_fields = ['agent_name', 'call_date', 'call_content']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return bad_request(
                message=f"缺少必填字段: {', '.join(missing_fields)}"
            )
        
        # 字段值校验
        call_duration = data.get('call_duration', 0)
        try:
            call_duration = int(call_duration)
        except (ValueError, TypeError):
            return bad_request(message="通话时长必须是整数")
        
        storage = get_quality_storage()
        
        record = {
            'agent_name': data['agent_name'],
            'call_date': data['call_date'],
            'call_duration': call_duration,
            'call_content': data['call_content'],
            'status': 'pending',
            'overall_score': None,
            'scores': {},
            'issues': [],
            'suggestions': [],
            'analyzed_by': None
        }
        
        result = storage.create(record)
        
        return success_response(data=result, message="质检记录创建成功", code=201)
    
    except Exception as e:
        current_app.logger.error(f"Create quality check error: {str(e)}")
        return internal_error(message="创建质检记录失败")


@quality_bp.route('/checks/<check_id>', methods=['GET'])
def get_check(check_id):
    """获取质检详情"""
    try:
        storage = get_quality_storage()
        check = storage.get(check_id)
        
        if not check:
            return not_found(message="质检记录不存在")
        
        return success_response(data=check)
    
    except Exception as e:
        current_app.logger.error(f"Get quality check error: {str(e)}")
        return internal_error(message="获取质检详情失败")


@quality_bp.route('/analyze', methods=['POST'])
def analyze_call():
    """AI质检分析"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        call_content = data.get('call_content')
        if not call_content:
            return bad_request(message="缺少通话内容(call_content)")
        
        if len(call_content.strip()) < 10:
            return bad_request(message="通话内容太短，至少需要10个字符")
        
        agent_name = data.get('agent_name')
        
        service = get_quality_service()
        result = service.analyze(call_content, agent_name)
        
        return success_response(data=result, message="质检分析完成")
    
    except ValueError as e:
        return bad_request(message=str(e))
    except Exception as e:
        current_app.logger.error(f"Analyze call error: {str(e)}")
        return internal_error(message="质检分析失败")


@quality_bp.route('/checks/<check_id>/analyze', methods=['POST'])
def analyze_existing_check(check_id):
    """对已有质检记录进行AI分析"""
    try:
        service = get_quality_service()
        result = service.analyze_and_save(check_id)
        
        return success_response(data=result, message="质检分析完成")
    
    except ValueError as e:
        return bad_request(message=str(e))
    except Exception as e:
        current_app.logger.error(f"Analyze existing check error: {str(e)}")
        return internal_error(message="质检分析失败")


@quality_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取质检统计数据"""
    try:
        # 获取日期范围参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_range = None
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range['start'] = start_date
            if end_date:
                date_range['end'] = end_date
        
        storage = get_quality_storage()
        stats = storage.get_statistics(date_range)
        
        return success_response(data=stats)
    
    except Exception as e:
        current_app.logger.error(f"Get quality statistics error: {str(e)}")
        return internal_error(message="获取统计数据失败")


@quality_bp.route('/agents/<agent_name>/statistics', methods=['GET'])
def get_agent_statistics(agent_name):
    """获取指定客服的质检统计"""
    try:
        storage = get_quality_storage()
        stats = storage.get_agent_statistics(agent_name)
        
        return success_response(data=stats)
    
    except Exception as e:
        current_app.logger.error(f"Get agent statistics error: {str(e)}")
        return internal_error(message="获取客服统计失败")
