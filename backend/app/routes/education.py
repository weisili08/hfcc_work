"""
投教内容API路由
提供投教内容管理和AI生成功能
"""

from flask import Blueprint, request, current_app

from app.utils.response import success_response, paginated_response, bad_request, not_found
from app.services.llm_service import LLMService
from app.services.education_service import EducationService
from app.storage.education_storage import EducationContentStorage

# 创建蓝图
education_bp = Blueprint('education', __name__)


def _get_education_service():
    """获取投教服务实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    llm_service = LLMService(current_app.config)
    storage = EducationContentStorage(data_dir)
    return EducationService(llm_service, storage)


@education_bp.route('/contents', methods=['GET'])
def list_contents():
    """
    投教内容列表
    
    支持category/audience/status过滤
    
    Query参数:
        - category: 分类筛选 (fund_basics/risk_management/market_knowledge/regulation)
        - target_audience: 受众筛选 (beginner/intermediate/advanced)
        - status: 状态筛选 (draft/review/published/archived)
        - keyword: 搜索关键词
        - page: 页码，默认1
        - page_size: 每页条数，默认20
    
    Returns:
        分页内容列表
    """
    try:
        # 获取查询参数
        category = request.args.get('category')
        target_audience = request.args.get('target_audience')
        status = request.args.get('status')
        keyword = request.args.get('keyword')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 参数校验
        if page < 1:
            return bad_request(message='页码必须大于0')
        if page_size < 1 or page_size > 100:
            return bad_request(message='每页条数必须在1-100之间')
        
        # 构建过滤条件
        filters = {}
        if category:
            filters['category'] = category
        if target_audience:
            filters['target_audience'] = target_audience
        if status:
            filters['status'] = status
        
        service = _get_education_service()
        
        # 如果有搜索关键词，使用搜索功能
        if keyword:
            items = service.storage.search_contents(keyword)
            return success_response(data={
                'items': items,
                'total': len(items),
                'keyword': keyword
            })
        
        # 分页查询
        result = service.list_contents(filters=filters, page=page, page_size=page_size)
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )
    
    except Exception as e:
        current_app.logger.error(f"List education contents failed: {str(e)}")
        return success_response(data={'items': [], 'total': 0})


@education_bp.route('/contents', methods=['POST'])
def create_content():
    """
    创建投教内容
    
    Request Body:
        - title: 标题 (必填)
        - category: 分类 (必填)
        - target_audience: 目标受众 (必填)
        - content: 内容正文 (必填)
        - format: 格式，默认article
        - tags: 标签列表
        - status: 状态，默认draft
    
    Returns:
        创建后的内容记录
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        # 必填字段校验
        required_fields = ['title', 'category', 'target_audience', 'content']
        for field in required_fields:
            if not data.get(field):
                return bad_request(message=f'缺少必填字段: {field}')
        
        # 构建内容数据
        content_data = {
            'title': data['title'],
            'category': data['category'],
            'target_audience': data['target_audience'],
            'content': data['content'],
            'format': data.get('format', 'article'),
            'tags': data.get('tags', []),
            'status': data.get('status', 'draft'),
            'view_count': 0,
            'like_count': 0
        }
        
        service = _get_education_service()
        created_by = data.get('created_by', 'system')
        result = service.save_content(content_data, created_by)
        
        return success_response(data=result, message='创建成功')
    
    except Exception as e:
        current_app.logger.error(f"Create education content failed: {str(e)}")
        return success_response(data={'error': str(e)})


@education_bp.route('/contents/<content_id>', methods=['GET'])
def get_content(content_id):
    """
    获取内容详情
    
    Args:
        content_id: 内容ID
    
    Returns:
        内容详情
    """
    try:
        service = _get_education_service()
        content = service.get_content(content_id)
        
        if not content:
            return not_found(message='内容不存在')
        
        # 增加浏览次数
        service.storage.increment_view_count(content_id)
        content['view_count'] = content.get('view_count', 0) + 1
        
        return success_response(data=content)
    
    except Exception as e:
        current_app.logger.error(f"Get education content failed: {str(e)}")
        return not_found(message='内容不存在')


@education_bp.route('/contents/<content_id>', methods=['PUT'])
def update_content(content_id):
    """
    更新内容
    
    Args:
        content_id: 内容ID
    
    Request Body:
        要更新的字段
    
    Returns:
        更新后的内容
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        service = _get_education_service()
        
        # 检查内容是否存在
        existing = service.get_content(content_id)
        if not existing:
            return not_found(message='内容不存在')
        
        # 更新字段（排除id和created_at）
        updates = {k: v for k, v in data.items() if k not in ['id', 'created_at']}
        
        result = service.storage.update_content(content_id, updates)
        
        return success_response(data=result, message='更新成功')
    
    except Exception as e:
        current_app.logger.error(f"Update education content failed: {str(e)}")
        return success_response(data={'error': str(e)})


@education_bp.route('/generate', methods=['POST'])
def generate_content():
    """
    AI生成投教内容
    
    Request Body:
        - topic: 主题 (必填)
        - category: 分类 (必填)
        - target_audience: 目标受众 (必填)
        - format: 格式，默认article
    
    Returns:
        生成的内容
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        # 必填字段校验
        topic = data.get('topic')
        category = data.get('category')
        target_audience = data.get('target_audience')
        
        if not topic:
            return bad_request(message='缺少必填字段: topic')
        if not category:
            return bad_request(message='缺少必填字段: category')
        if not target_audience:
            return bad_request(message='缺少必填字段: target_audience')
        
        content_format = data.get('format', 'article')
        
        service = _get_education_service()
        result = service.generate_content(topic, category, target_audience, content_format)
        
        return success_response(data=result, message='生成成功')
    
    except Exception as e:
        current_app.logger.error(f"Generate education content failed: {str(e)}")
        return success_response(data={'error': str(e)})


@education_bp.route('/quiz/generate', methods=['POST'])
def generate_quiz():
    """
    生成投教测验
    
    Request Body:
        - topic: 测验主题 (必填)
        - difficulty: 难度 (easy/medium/hard)，默认medium
        - count: 题目数量，默认5
    
    Returns:
        生成的测验
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(message='请求体不能为空')
        
        topic = data.get('topic')
        if not topic:
            return bad_request(message='缺少必填字段: topic')
        
        difficulty = data.get('difficulty', 'medium')
        count = data.get('count', 5)
        
        # 限制题目数量
        if count < 1:
            count = 1
        elif count > 20:
            count = 20
        
        service = _get_education_service()
        result = service.generate_quiz(topic, difficulty, count)
        
        return success_response(data=result, message='生成成功')
    
    except Exception as e:
        current_app.logger.error(f"Generate quiz failed: {str(e)}")
        return success_response(data={'error': str(e)})


@education_bp.route('/contents/<content_id>/like', methods=['POST'])
def like_content(content_id):
    """
    点赞内容
    
    Args:
        content_id: 内容ID
    
    Returns:
        更新后的点赞数
    """
    try:
        service = _get_education_service()
        
        # 检查内容是否存在
        content = service.get_content(content_id)
        if not content:
            return not_found(message='内容不存在')
        
        # 增加点赞数
        result = service.storage.increment_like_count(content_id)
        
        return success_response(data={
            'content_id': content_id,
            'like_count': result.get('like_count', 0)
        }, message='点赞成功')
    
    except Exception as e:
        current_app.logger.error(f"Like content failed: {str(e)}")
        return success_response(data={'error': str(e)})
