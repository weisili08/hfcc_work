"""
投诉管理API路由模块
提供投诉相关的RESTful API接口
"""

from flask import Blueprint, request, current_app

from app.storage.complaint_storage import ComplaintStorage
from app.utils.response import (
    success_response, paginated_response, 
    bad_request, not_found, internal_error
)

complaint_bp = Blueprint('complaint', __name__)


def get_complaint_storage():
    """获取投诉存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return ComplaintStorage(data_dir)


@complaint_bp.route('/', methods=['GET'])
def list_complaints():
    """
    获取投诉列表
    
    支持过滤：status, type, priority
    支持分页：page, page_size
    """
    try:
        # 获取查询参数
        status = request.args.get('status')
        complaint_type = request.args.get('type')
        priority = request.args.get('priority')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤条件
        filters = {}
        if status:
            filters['status'] = status
        if complaint_type:
            filters['type'] = complaint_type
        if priority:
            filters['priority'] = priority
        
        # 限制分页大小
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        
        storage = get_complaint_storage()
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
        current_app.logger.error(f"List complaints error: {str(e)}")
        return internal_error(message="获取投诉列表失败")


@complaint_bp.route('/', methods=['POST'])
def create_complaint():
    """创建投诉"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        required_fields = ['title', 'customer_name', 'type', 'description']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return bad_request(
                message=f"缺少必填字段: {', '.join(missing_fields)}"
            )
        
        # 字段值校验
        valid_types = ['product', 'service', 'system', 'other']
        valid_priorities = ['high', 'medium', 'low']
        
        if data.get('type') not in valid_types:
            return bad_request(
                message=f"无效的投诉类型，必须是: {', '.join(valid_types)}"
            )
        
        priority = data.get('priority', 'medium')
        if priority not in valid_priorities:
            return bad_request(
                message=f"无效的优先级，必须是: {', '.join(valid_priorities)}"
            )
        
        # 构建投诉记录
        complaint = {
            'title': data['title'],
            'customer_name': data['customer_name'],
            'customer_phone': data.get('customer_phone', ''),
            'type': data['type'],
            'description': data['description'],
            'status': 'pending',
            'priority': priority,
            'assignee': data.get('assignee', ''),
            'resolution': '',
            'created_by': data.get('created_by', 'system')
        }
        
        storage = get_complaint_storage()
        result = storage.create(complaint)
        
        return success_response(data=result, message="投诉创建成功", code=201)
    
    except Exception as e:
        current_app.logger.error(f"Create complaint error: {str(e)}")
        return internal_error(message="创建投诉失败")


@complaint_bp.route('/<complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    """获取投诉详情"""
    try:
        storage = get_complaint_storage()
        complaint = storage.get(complaint_id)
        
        if not complaint:
            return not_found(message="投诉不存在")
        
        return success_response(data=complaint)
    
    except Exception as e:
        current_app.logger.error(f"Get complaint error: {str(e)}")
        return internal_error(message="获取投诉详情失败")


@complaint_bp.route('/<complaint_id>', methods=['PUT'])
def update_complaint(complaint_id):
    """更新投诉"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        storage = get_complaint_storage()
        
        # 检查投诉是否存在
        existing = storage.get(complaint_id)
        if not existing:
            return not_found(message="投诉不存在")
        
        # 过滤可更新字段
        allowed_fields = [
            'title', 'customer_name', 'customer_phone', 
            'type', 'description', 'priority', 'assignee'
        ]
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        # 字段值校验
        if 'type' in updates and updates['type'] not in ['product', 'service', 'system', 'other']:
            return bad_request(message="无效的投诉类型")
        
        if 'priority' in updates and updates['priority'] not in ['high', 'medium', 'low']:
            return bad_request(message="无效的优先级")
        
        result = storage.update(complaint_id, updates)
        
        if result:
            return success_response(data=result, message="投诉更新成功")
        else:
            return internal_error(message="更新投诉失败")
    
    except Exception as e:
        current_app.logger.error(f"Update complaint error: {str(e)}")
        return internal_error(message="更新投诉失败")


@complaint_bp.route('/<complaint_id>/assign', methods=['POST'])
def assign_complaint(complaint_id):
    """分配投诉"""
    try:
        data = request.get_json() or {}
        assignee = data.get('assignee')
        
        if not assignee:
            return bad_request(message="缺少处理人(assignee)")
        
        storage = get_complaint_storage()
        
        # 检查投诉是否存在
        existing = storage.get(complaint_id)
        if not existing:
            return not_found(message="投诉不存在")
        
        result = storage.assign(complaint_id, assignee)
        
        if result:
            return success_response(data=result, message="投诉分配成功")
        else:
            return internal_error(message="分配投诉失败")
    
    except Exception as e:
        current_app.logger.error(f"Assign complaint error: {str(e)}")
        return internal_error(message="分配投诉失败")


@complaint_bp.route('/<complaint_id>/escalate', methods=['POST'])
def escalate_complaint(complaint_id):
    """升级投诉"""
    try:
        storage = get_complaint_storage()
        
        # 检查投诉是否存在
        existing = storage.get(complaint_id)
        if not existing:
            return not_found(message="投诉不存在")
        
        # 检查状态是否允许升级
        if existing['status'] in ['resolved', 'closed']:
            return bad_request(message="已解决或已关闭的投诉不能升级")
        
        result = storage.escalate(complaint_id)
        
        if result:
            return success_response(data=result, message="投诉升级成功")
        else:
            return internal_error(message="升级投诉失败")
    
    except Exception as e:
        current_app.logger.error(f"Escalate complaint error: {str(e)}")
        return internal_error(message="升级投诉失败")


@complaint_bp.route('/<complaint_id>/resolve', methods=['POST'])
def resolve_complaint(complaint_id):
    """解决投诉"""
    try:
        data = request.get_json() or {}
        resolution = data.get('resolution')
        
        if not resolution:
            return bad_request(message="缺少解决方案(resolution)")
        
        storage = get_complaint_storage()
        
        # 检查投诉是否存在
        existing = storage.get(complaint_id)
        if not existing:
            return not_found(message="投诉不存在")
        
        # 检查状态是否允许解决
        if existing['status'] == 'closed':
            return bad_request(message="已关闭的投诉不能解决")
        
        result = storage.resolve(complaint_id, resolution)
        
        if result:
            return success_response(data=result, message="投诉解决成功")
        else:
            return internal_error(message="解决投诉失败")
    
    except Exception as e:
        current_app.logger.error(f"Resolve complaint error: {str(e)}")
        return internal_error(message="解决投诉失败")


@complaint_bp.route('/<complaint_id>/close', methods=['POST'])
def close_complaint(complaint_id):
    """关闭投诉"""
    try:
        storage = get_complaint_storage()
        
        # 检查投诉是否存在
        existing = storage.get(complaint_id)
        if not existing:
            return not_found(message="投诉不存在")
        
        result = storage.close(complaint_id)
        
        if result:
            return success_response(data=result, message="投诉关闭成功")
        else:
            return internal_error(message="关闭投诉失败")
    
    except Exception as e:
        current_app.logger.error(f"Close complaint error: {str(e)}")
        return internal_error(message="关闭投诉失败")


@complaint_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取投诉统计数据"""
    try:
        storage = get_complaint_storage()
        stats = storage.get_statistics()
        
        return success_response(data=stats)
    
    except Exception as e:
        current_app.logger.error(f"Get statistics error: {str(e)}")
        return internal_error(message="获取统计数据失败")
