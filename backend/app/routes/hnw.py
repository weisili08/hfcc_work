"""
高净值客户服务模块路由
提供高净值客户管理、资产配置、客户关怀、活动策划等API
"""

import os
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, current_app

from app.utils.response import (
    success_response, paginated_response, 
    bad_request, not_found, internal_error
)
from app.storage.hnw_storage import (
    HNWCustomerStorage, HNWServiceStorage, 
    HNWEventStorage, HNWTouchpointStorage
)
from app.services.allocation_service import AllocationService
from app.services.care_service import CareService
from app.services.llm_service import LLMService


# 创建蓝图
hnw_bp = Blueprint('hnw', __name__)


# 初始化存储实例
_customer_storage = None
_service_storage = None
_event_storage = None
_touchpoint_storage = None
_allocation_service = None
_care_service = None


def _get_customer_storage():
    """获取客户存储实例（懒加载）"""
    global _customer_storage
    if _customer_storage is None:
        data_dir = current_app.config.get('DATA_DIR', './data')
        _customer_storage = HNWCustomerStorage(data_dir)
    return _customer_storage


def _get_service_storage():
    """获取服务记录存储实例（懒加载）"""
    global _service_storage
    if _service_storage is None:
        data_dir = current_app.config.get('DATA_DIR', './data')
        _service_storage = HNWServiceStorage(data_dir)
    return _service_storage


def _get_event_storage():
    """获取活动记录存储实例（懒加载）"""
    global _event_storage
    if _event_storage is None:
        data_dir = current_app.config.get('DATA_DIR', './data')
        _event_storage = HNWEventStorage(data_dir)
    return _event_storage


def _get_touchpoint_storage():
    """获取触达任务存储实例（懒加载）"""
    global _touchpoint_storage
    if _touchpoint_storage is None:
        data_dir = current_app.config.get('DATA_DIR', './data')
        _touchpoint_storage = HNWTouchpointStorage(data_dir)
    return _touchpoint_storage


def _get_allocation_service():
    """获取资产配置服务实例（懒加载）"""
    global _allocation_service
    if _allocation_service is None:
        llm_service = _get_llm_service()
        _allocation_service = AllocationService(llm_service)
    return _allocation_service


def _get_care_service():
    """获取客户关怀服务实例（懒加载）"""
    global _care_service
    if _care_service is None:
        llm_service = _get_llm_service()
        _care_service = CareService(llm_service)
    return _care_service


def _get_llm_service():
    """获取LLM服务实例"""
    config = {
        'LLM_API_KEY': current_app.config.get('LLM_API_KEY', ''),
        'LLM_API_URL': current_app.config.get('LLM_API_URL', ''),
        'LLM_MODEL': current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_TIMEOUT': current_app.config.get('LLM_TIMEOUT', 30),
        'LLM_BACKUP_API_KEY': current_app.config.get('LLM_BACKUP_API_KEY', ''),
        'LLM_BACKUP_API_URL': current_app.config.get('LLM_BACKUP_API_URL', ''),
        'LLM_BACKUP_MODEL': current_app.config.get('LLM_BACKUP_MODEL', '')
    }
    return LLMService(config)


# ==================== 客户管理API ====================

@hnw_bp.route('/customers', methods=['GET'])
def get_customers():
    """
    获取高净值客户列表
    
    Query参数:
    - tier: 客户等级筛选 (diamond/platinum/gold)
    - risk_level: 风险等级筛选 (conservative/moderate/aggressive)
    - manager_id: 客户经理筛选
    - page: 页码，默认1
    - page_size: 每页条数，默认20
    """
    try:
        storage = _get_customer_storage()
        
        # 获取查询参数
        tier = request.args.get('tier')
        risk_level = request.args.get('risk_level')
        manager_id = request.args.get('manager_id')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤器
        filters = {}
        if tier:
            filters['tier'] = tier
        if risk_level:
            filters['risk_level'] = risk_level
        if manager_id:
            filters['manager_id'] = manager_id
        
        # 查询数据
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
        current_app.logger.error(f"Error getting customers: {e}")
        return internal_error(message="获取客户列表失败")


@hnw_bp.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    获取客户详情
    
    Path参数:
    - customer_id: 客户ID
    """
    try:
        storage = _get_customer_storage()
        customer = storage.get(customer_id)
        
        if not customer:
            return not_found(
                error_code="CUSTOMER_NOT_FOUND",
                message="客户不存在",
                details={"customer_id": customer_id}
            )
        
        return success_response(data=customer)
    
    except Exception as e:
        current_app.logger.error(f"Error getting customer: {e}")
        return internal_error(message="获取客户详情失败")


@hnw_bp.route('/customers', methods=['POST'])
def create_customer():
    """
    创建高净值客户
    
    Request Body:
    - name: 客户姓名（必填）
    - phone: 联系电话（必填）
    - email: 邮箱
    - risk_level: 风险等级（必填）
    - aum: 资产管理规模（必填）
    - tier: 客户等级（必填）
    - manager_id: 客户经理ID
    - tags: 标签列表
    - preferences: 偏好设置
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        required_fields = ['name', 'phone', 'risk_level', 'aum', 'tier']
        missing_fields = [f for f in required_fields if not data.get(f)]
        
        if missing_fields:
            return bad_request(
                error_code="MISSING_REQUIRED_FIELDS",
                message="缺少必填字段",
                details={"missing_fields": missing_fields}
            )
        
        # 字段值校验
        valid_risk_levels = ['conservative', 'moderate', 'aggressive']
        if data['risk_level'] not in valid_risk_levels:
            return bad_request(
                error_code="INVALID_RISK_LEVEL",
                message="无效的风险等级",
                details={"valid_values": valid_risk_levels}
            )
        
        valid_tiers = ['diamond', 'platinum', 'gold']
        if data['tier'] not in valid_tiers:
            return bad_request(
                error_code="INVALID_TIER",
                message="无效的客户等级",
                details={"valid_values": valid_tiers}
            )
        
        storage = _get_customer_storage()
        customer = storage.create(data)
        
        return success_response(data=customer, code=201)
    
    except Exception as e:
        current_app.logger.error(f"Error creating customer: {e}")
        return internal_error(message="创建客户失败")


@hnw_bp.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """
    更新客户信息
    
    Path参数:
    - customer_id: 客户ID
    
    Request Body:
    - 可更新字段：name, phone, email, risk_level, aum, tier, manager_id, tags, preferences, status
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        storage = _get_customer_storage()
        
        # 检查客户是否存在
        customer = storage.get(customer_id)
        if not customer:
            return not_found(
                error_code="CUSTOMER_NOT_FOUND",
                message="客户不存在",
                details={"customer_id": customer_id}
            )
        
        # 字段值校验
        if 'risk_level' in data:
            valid_risk_levels = ['conservative', 'moderate', 'aggressive']
            if data['risk_level'] not in valid_risk_levels:
                return bad_request(
                    error_code="INVALID_RISK_LEVEL",
                    message="无效的风险等级",
                    details={"valid_values": valid_risk_levels}
                )
        
        if 'tier' in data:
            valid_tiers = ['diamond', 'platinum', 'gold']
            if data['tier'] not in valid_tiers:
                return bad_request(
                    error_code="INVALID_TIER",
                    message="无效的客户等级",
                    details={"valid_values": valid_tiers}
                )
        
        if 'status' in data:
            valid_statuses = ['active', 'inactive']
            if data['status'] not in valid_statuses:
                return bad_request(
                    error_code="INVALID_STATUS",
                    message="无效的状态",
                    details={"valid_values": valid_statuses}
                )
        
        updated_customer = storage.update(customer_id, data)
        
        return success_response(data=updated_customer)
    
    except Exception as e:
        current_app.logger.error(f"Error updating customer: {e}")
        return internal_error(message="更新客户失败")


# ==================== 资产配置API ====================

@hnw_bp.route('/allocation', methods=['POST'])
def generate_allocation():
    """
    生成资产配置建议
    
    Request Body（方式1 - 通过customer_id）:
    - customer_id: 客户ID
    
    Request Body（方式2 - 直接传客户画像）:
    - risk_level: 风险等级
    - aum: 资产管理规模
    - age_range: 年龄段
    - investment_horizon: 投资期限
    - preferences: 偏好设置
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        customer_profile = None
        
        # 方式1：通过customer_id获取客户信息
        if 'customer_id' in data:
            storage = _get_customer_storage()
            customer = storage.get(data['customer_id'])
            
            if not customer:
                return not_found(
                    error_code="CUSTOMER_NOT_FOUND",
                    message="客户不存在",
                    details={"customer_id": data['customer_id']}
                )
            
            customer_profile = {
                'risk_level': customer.get('risk_level', 'moderate'),
                'aum': customer.get('aum', 0),
                'age_range': data.get('age_range', '40-50'),
                'investment_horizon': data.get('investment_horizon', '中长期'),
                'preferences': customer.get('preferences', {})
            }
        else:
            # 方式2：直接传客户画像
            if 'risk_level' not in data or 'aum' not in data:
                return bad_request(
                    error_code="MISSING_REQUIRED_FIELDS",
                    message="缺少必填字段：risk_level, aum",
                    details={"required": ["risk_level", "aum"]}
                )
            
            customer_profile = {
                'risk_level': data['risk_level'],
                'aum': data['aum'],
                'age_range': data.get('age_range', '40-50'),
                'investment_horizon': data.get('investment_horizon', '中长期'),
                'preferences': data.get('preferences', {})
            }
        
        service = _get_allocation_service()
        allocation = service.generate_allocation(customer_profile)
        
        # 添加建议ID和时间戳
        result = {
            'advice_id': f"adv_{uuid.uuid4().hex[:12]}",
            'customer_portrait': customer_profile,
            'current_analysis': {
                'total_aum': customer_profile['aum'],
                'allocation': [],
                'risk_exposure': customer_profile['risk_level']
            },
            'recommendations': {
                'target_allocation': [
                    {'asset_class': '权益类', 'percentage': allocation['allocation_plan']['equity_pct'],
                     'products': [p['products'][0] for p in allocation['recommended_products'] if '股' in p['category'] or '混合' in p['category']][:2]},
                    {'asset_class': '固收类', 'percentage': allocation['allocation_plan']['bond_pct'],
                     'products': [p['products'][0] for p in allocation['recommended_products'] if '债' in p['category']][:2]},
                    {'asset_class': '货币市场', 'percentage': allocation['allocation_plan']['money_market_pct'],
                     'products': ['XX货币基金']},
                    {'asset_class': '另类投资', 'percentage': allocation['allocation_plan']['alternative_pct'],
                     'products': ['XX黄金ETF', 'XXREITs']}
                ],
                'adjustment_reason': allocation['rationale']
            },
            'risk_warning': '；'.join(allocation['risk_warnings']),
            'disclaimer': '以上建议仅供参考，不构成投资建议。投资有风险，入市需谨慎。',
            'ai_generated': allocation.get('ai_generated', False),
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return success_response(data=result)
    
    except Exception as e:
        current_app.logger.error(f"Error generating allocation: {e}")
        return internal_error(message="生成资产配置建议失败")


# ==================== 服务记录API ====================

@hnw_bp.route('/services', methods=['GET'])
def get_services():
    """
    获取服务记录列表
    
    Query参数:
    - customer_id: 客户ID筛选
    - service_type: 服务类型筛选 (consultation/allocation/review/care)
    - created_by: 创建人筛选
    - page: 页码，默认1
    - page_size: 每页条数，默认20
    """
    try:
        storage = _get_service_storage()
        
        # 获取查询参数
        customer_id = request.args.get('customer_id')
        service_type = request.args.get('service_type')
        created_by = request.args.get('created_by')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤器
        filters = {}
        if customer_id:
            filters['customer_id'] = customer_id
        if service_type:
            filters['service_type'] = service_type
        if created_by:
            filters['created_by'] = created_by
        
        # 查询数据
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
        current_app.logger.error(f"Error getting services: {e}")
        return internal_error(message="获取服务记录失败")


@hnw_bp.route('/services', methods=['POST'])
def create_service():
    """
    创建服务记录
    
    Request Body:
    - customer_id: 客户ID（必填）
    - service_type: 服务类型（必填）
    - description: 服务描述
    - result: 服务结果
    - next_action: 后续行动
    - created_by: 创建人
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        if not data.get('customer_id'):
            return bad_request(
                error_code="MISSING_CUSTOMER_ID",
                message="缺少客户ID"
            )
        
        if not data.get('service_type'):
            return bad_request(
                error_code="MISSING_SERVICE_TYPE",
                message="缺少服务类型"
            )
        
        # 验证客户是否存在
        customer_storage = _get_customer_storage()
        customer = customer_storage.get(data['customer_id'])
        if not customer:
            return not_found(
                error_code="CUSTOMER_NOT_FOUND",
                message="客户不存在",
                details={"customer_id": data['customer_id']}
            )
        
        # 验证服务类型
        valid_types = ['consultation', 'allocation', 'review', 'care']
        if data['service_type'] not in valid_types:
            return bad_request(
                error_code="INVALID_SERVICE_TYPE",
                message="无效的服务类型",
                details={"valid_values": valid_types}
            )
        
        storage = _get_service_storage()
        service = storage.create(data)
        
        return success_response(data=service, code=201)
    
    except Exception as e:
        current_app.logger.error(f"Error creating service: {e}")
        return internal_error(message="创建服务记录失败")


# ==================== 客户关怀API ====================

@hnw_bp.route('/care/plan', methods=['POST'])
def generate_care_plan():
    """
    生成关怀计划
    
    Request Body:
    - customer_id: 客户ID（必填）
    - occasion: 关怀场合（必填）
    - event_date: 事件日期
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        if not data.get('customer_id'):
            return bad_request(
                error_code="MISSING_CUSTOMER_ID",
                message="缺少客户ID"
            )
        
        if not data.get('occasion'):
            return bad_request(
                error_code="MISSING_OCCASION",
                message="缺少关怀场合"
            )
        
        # 验证客户是否存在
        storage = _get_customer_storage()
        customer = storage.get(data['customer_id'])
        
        if not customer:
            return not_found(
                error_code="CUSTOMER_NOT_FOUND",
                message="客户不存在",
                details={"customer_id": data['customer_id']}
            )
        
        # 验证occasion
        valid_occasions = ['birthday', 'anniversary', 'market_volatility', 'redemption', 'festival']
        if data['occasion'] not in valid_occasions:
            return bad_request(
                error_code="INVALID_OCCASION",
                message="无效的关怀场合",
                details={"valid_values": valid_occasions}
            )
        
        # 构建客户信息
        customer_info = {
            'name': customer.get('name', ''),
            'tier': customer.get('tier', 'gold'),
            'risk_level': customer.get('risk_level', 'moderate'),
            'aum': customer.get('aum', 0),
            'preferences': customer.get('preferences', {}),
            'investment_date': customer.get('created_at', '')
        }
        
        service = _get_care_service()
        care_plan = service.generate_care_plan(customer_info, data['occasion'])
        
        # 添加计划ID
        result = {
            'plan_id': f"care_{uuid.uuid4().hex[:12]}",
            'touchpoint_type': data['occasion'],
            'customer_id': data['customer_id'],
            'care_plan': care_plan.get('care_plan', {}),
            'ai_generated': care_plan.get('ai_generated', False),
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return success_response(data=result)
    
    except Exception as e:
        current_app.logger.error(f"Error generating care plan: {e}")
        return internal_error(message="生成关怀计划失败")


# ==================== 活动管理API ====================

@hnw_bp.route('/events', methods=['GET'])
def get_events():
    """
    获取活动列表
    
    Query参数:
    - status: 状态筛选 (planning/confirmed/completed/cancelled)
    - type: 活动类型筛选 (online/offline/mixed)
    - target_tier: 目标客户等级筛选
    - page: 页码，默认1
    - page_size: 每页条数，默认20
    """
    try:
        storage = _get_event_storage()
        
        # 获取查询参数
        status = request.args.get('status')
        event_type = request.args.get('type')
        target_tier = request.args.get('target_tier')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤器
        filters = {}
        if status:
            filters['status'] = status
        if event_type:
            filters['type'] = event_type
        
        # 查询数据
        if target_tier:
            result = storage.get_by_target_tier(target_tier, page, page_size)
        else:
            result = storage.list(
                filters=filters if filters else None,
                page=page,
                page_size=page_size,
                sort_by='date',
                sort_order='asc'
            )
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
    
    except Exception as e:
        current_app.logger.error(f"Error getting events: {e}")
        return internal_error(message="获取活动列表失败")


@hnw_bp.route('/events', methods=['POST'])
def create_event():
    """
    创建活动
    
    Request Body:
    - title: 活动标题（必填）
    - type: 活动类型（必填）
    - description: 活动描述
    - target_tier: 目标客户等级列表
    - date: 活动日期
    - location: 活动地点
    - budget: 预算
    - created_by: 创建人
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        if not data.get('title'):
            return bad_request(
                error_code="MISSING_TITLE",
                message="缺少活动标题"
            )
        
        if not data.get('type'):
            return bad_request(
                error_code="MISSING_TYPE",
                message="缺少活动类型"
            )
        
        # 验证活动类型
        valid_types = ['online', 'offline', 'mixed']
        if data['type'] not in valid_types:
            return bad_request(
                error_code="INVALID_TYPE",
                message="无效的活动类型",
                details={"valid_values": valid_types}
            )
        
        storage = _get_event_storage()
        event = storage.create(data)
        
        return success_response(data=event, code=201)
    
    except Exception as e:
        current_app.logger.error(f"Error creating event: {e}")
        return internal_error(message="创建活动失败")


@hnw_bp.route('/events/plan', methods=['POST'])
def plan_event():
    """
    AI策划活动
    
    Request Body:
    - event_type: 活动类型（必填）
    - target_tier: 目标客户等级（必填）
    - budget: 预算（必填）
    - expected_attendees: 预计参与人数
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        required_fields = ['event_type', 'target_tier', 'budget']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return bad_request(
                error_code="MISSING_REQUIRED_FIELDS",
                message="缺少必填字段",
                details={"missing_fields": missing_fields}
            )
        
        # 验证活动类型
        valid_types = ['fixed_income', 'equity_roadshow', 'client_appreciation', 'salon']
        if data['event_type'] not in valid_types:
            return bad_request(
                error_code="INVALID_EVENT_TYPE",
                message="无效的活动类型",
                details={"valid_values": valid_types}
            )
        
        # 获取目标客户
        customer_storage = _get_customer_storage()
        target_customers_result = customer_storage.get_by_tier(
            data['target_tier'], 
            page=1, 
            page_size=data.get('expected_attendees', 50)
        )
        target_customers = target_customers_result.get('items', [])
        
        service = _get_care_service()
        event_plan = service.plan_event(
            data['event_type'],
            target_customers,
            data['budget']
        )
        
        # 添加计划ID
        result = {
            'plan_id': f"ep_{uuid.uuid4().hex[:12]}",
            **event_plan,
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return success_response(data=result)
    
    except Exception as e:
        current_app.logger.error(f"Error planning event: {e}")
        return internal_error(message="活动策划失败")


# ==================== 触达任务API ====================

@hnw_bp.route('/touchpoints', methods=['GET'])
def get_touchpoints():
    """
    获取触达任务列表
    
    Query参数:
    - customer_id: 客户ID筛选
    - touchpoint_type: 触达类型筛选
    - status: 状态筛选 (pending/completed/ignored)
    - upcoming_days: 未来N天内，默认30
    - page: 页码，默认1
    - page_size: 每页条数，默认20
    """
    try:
        storage = _get_touchpoint_storage()
        
        # 获取查询参数
        customer_id = request.args.get('customer_id')
        touchpoint_type = request.args.get('touchpoint_type')
        status = request.args.get('status')
        upcoming_days = request.args.get('upcoming_days', 30, type=int)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤器
        filters = {}
        if customer_id:
            filters['customer_id'] = customer_id
        if touchpoint_type:
            filters['touchpoint_type'] = touchpoint_type
        if status:
            filters['status'] = status
        
        # 查询数据
        if not filters and upcoming_days:
            # 获取即将到期的任务
            result = storage.get_upcoming(upcoming_days, page, page_size)
        else:
            result = storage.list(
                filters=filters if filters else None,
                page=page,
                page_size=page_size,
                sort_by='days_until',
                sort_order='asc'
            )
        
        # 汇总统计
        summary = {
            'total_upcoming': result['total'],
            'by_type': {}
        }
        
        for item in result['items']:
            tp_type = item.get('touchpoint_type', 'other')
            summary['by_type'][tp_type] = summary['by_type'].get(tp_type, 0) + 1
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size'],
            extra_data={'summary': summary}
        )
    
    except Exception as e:
        current_app.logger.error(f"Error getting touchpoints: {e}")
        return internal_error(message="获取触达任务失败")


@hnw_bp.route('/touchpoints/generate', methods=['POST'])
def generate_touchpoint():
    """
    生成触达话术
    
    Request Body:
    - customer_id: 客户ID（必填）
    - trigger: 触发事件（必填）
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        if not data.get('customer_id'):
            return bad_request(
                error_code="MISSING_CUSTOMER_ID",
                message="缺少客户ID"
            )
        
        if not data.get('trigger'):
            return bad_request(
                error_code="MISSING_TRIGGER",
                message="缺少触发事件"
            )
        
        # 验证客户是否存在
        storage = _get_customer_storage()
        customer = storage.get(data['customer_id'])
        
        if not customer:
            return not_found(
                error_code="CUSTOMER_NOT_FOUND",
                message="客户不存在",
                details={"customer_id": data['customer_id']}
            )
        
        # 验证触发事件
        valid_triggers = ['large_redemption', 'no_contact', 'market_volatility', 'birthday', 'anniversary']
        if data['trigger'] not in valid_triggers:
            return bad_request(
                error_code="INVALID_TRIGGER",
                message="无效的触发事件",
                details={"valid_values": valid_triggers}
            )
        
        # 构建客户信息
        customer_info = {
            'name': customer.get('name', ''),
            'tier': customer.get('tier', 'gold'),
            'risk_level': customer.get('risk_level', 'moderate'),
            'aum': customer.get('aum', 0),
            'preferences': customer.get('preferences', {})
        }
        
        service = _get_care_service()
        script = service.generate_touchpoint_script(customer_info, data['trigger'])
        
        # 添加任务ID
        result = {
            'touchpoint_id': f"tp_{uuid.uuid4().hex[:12]}",
            'customer_id': data['customer_id'],
            'trigger_event': data['trigger'],
            **script,
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return success_response(data=result)
    
    except Exception as e:
        current_app.logger.error(f"Error generating touchpoint: {e}")
        return internal_error(message="生成触达话术失败")
