"""
话术生成API路由模块
提供话术生成、历史记录、评分等接口
"""

from flask import Blueprint, request, current_app

from app.services.script_service import ScriptService
from app.storage.script_storage import ScriptStorage
from app.services.llm_service import LLMService
from app.utils.response import (
    success_response, paginated_response,
    bad_request, not_found, internal_error
)

script_bp = Blueprint('script', __name__)


def get_script_service():
    """获取话术服务实例"""
    config = {
        'LLM_API_KEY': current_app.config.get('LLM_API_KEY', ''),
        'LLM_API_URL': current_app.config.get('LLM_API_URL', ''),
        'LLM_MODEL': current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_TIMEOUT': current_app.config.get('LLM_TIMEOUT', 30)
    }
    llm_service = LLMService(config)
    return ScriptService(llm_service)


def get_script_storage():
    """获取话术存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return ScriptStorage(data_dir)


@script_bp.route('/generate', methods=['POST'])
def generate_script():
    """生成话术"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        scenario = data.get('scenario')
        if not scenario:
            return bad_request(message="缺少场景参数(scenario)")
        
        context = data.get('context', {})
        style = data.get('style', 'professional')
        
        # 调用服务生成话术
        service = get_script_service()
        result = service.generate(scenario, context, style)
        
        # 保存生成记录
        storage = get_script_storage()
        record = {
            'scenario': scenario,
            'context': context,
            'style': style,
            'content': result['generated_script'],
            'rating': None,
            'created_by': data.get('created_by', 'system')
        }
        saved = storage.create(record)
        
        # 添加ID到返回结果
        result['id'] = saved['id']
        result['created_at'] = saved['created_at']
        
        return success_response(data=result, message="话术生成成功")
    
    except ValueError as e:
        return bad_request(message=str(e))
    except Exception as e:
        current_app.logger.error(f"Generate script error: {str(e)}")
        return internal_error(message="生成话术失败")


@script_bp.route('/', methods=['GET'])
def list_scripts():
    """获取话术历史列表"""
    try:
        # 获取查询参数
        scenario = request.args.get('scenario')
        style = request.args.get('style')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤条件
        filters = {}
        if scenario:
            filters['scenario'] = scenario
        if style:
            filters['style'] = style
        
        # 限制分页大小
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        
        storage = get_script_storage()
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
        current_app.logger.error(f"List scripts error: {str(e)}")
        return internal_error(message="获取话术列表失败")


@script_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    """获取场景列表"""
    try:
        service = get_script_service()
        scenarios = service.get_scenarios()
        
        return success_response(data=scenarios)
    
    except Exception as e:
        current_app.logger.error(f"Get scenarios error: {str(e)}")
        return internal_error(message="获取场景列表失败")


@script_bp.route('/<script_id>/rate', methods=['POST'])
def rate_script(script_id):
    """评分话术"""
    try:
        data = request.get_json() or {}
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        # 校验评分
        if rating is None:
            return bad_request(message="缺少评分参数(rating)")
        
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            return bad_request(message="评分必须是整数")
        
        if not 1 <= rating <= 5:
            return bad_request(message="评分必须在1-5之间")
        
        storage = get_script_storage()
        
        # 检查话术是否存在
        existing = storage.get(script_id)
        if not existing:
            return not_found(message="话术记录不存在")
        
        result = storage.update_rating(script_id, rating, comment)
        
        if result:
            return success_response(data=result, message="评分成功")
        else:
            return internal_error(message="评分失败")
    
    except ValueError as e:
        return bad_request(message=str(e))
    except Exception as e:
        current_app.logger.error(f"Rate script error: {str(e)}")
        return internal_error(message="评分失败")


@script_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取话术统计数据"""
    try:
        storage = get_script_storage()
        stats = storage.get_statistics()
        
        return success_response(data=stats)
    
    except Exception as e:
        current_app.logger.error(f"Get script statistics error: {str(e)}")
        return internal_error(message="获取统计数据失败")
