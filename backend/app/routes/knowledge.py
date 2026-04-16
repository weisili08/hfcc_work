"""
知识库管理API路由模块
提供知识库和文档的CRUD接口
"""

import logging
from flask import Blueprint, request, current_app

from app.utils.response import (
    success_response, bad_request, not_found, 
    internal_error, paginated_response
)
from app.utils.auth import login_required, get_current_user
from app.storage.kb_storage import KnowledgeBaseStorage
from app.storage.kb_doc_storage import KBDocumentStorage


logger = logging.getLogger(__name__)

# 创建蓝图
knowledge_bp = Blueprint('knowledge', __name__)


def get_kb_storage():
    """获取知识库存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return KnowledgeBaseStorage(data_dir)


def get_doc_storage():
    """获取文档存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return KBDocumentStorage(data_dir)


# ==================== 知识库管理接口 ====================

@knowledge_bp.route('/', methods=['GET'])
@login_required
def list_knowledge_bases():
    """
    获取知识库列表
    
    查询参数:
        - page: 页码（默认1）
        - page_size: 每页条数（默认20）
        - category: 按分类过滤
        - status: 按状态过滤
    """
    try:
        # 解析查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        category = request.args.get('category')
        status = request.args.get('status')
        
        # 构建过滤条件
        filters = {}
        if category:
            filters['category'] = category
        if status:
            filters['status'] = status
        
        # 查询数据
        kb_storage = get_kb_storage()
        result = kb_storage.list(
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
        logger.error(f"List knowledge bases error: {str(e)}")
        return internal_error(
            error_code="LIST_KB_ERROR",
            message="获取知识库列表失败"
        )


@knowledge_bp.route('/', methods=['POST'])
@login_required
def create_knowledge_base():
    """
    创建知识库
    
    请求体:
        {
            "name": "知识库名称",
            "description": "知识库描述",
            "category": "分类"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        # 必填字段校验
        name = data.get('name', '').strip()
        if not name:
            return bad_request(
                error_code="MISSING_NAME",
                message="知识库名称不能为空"
            )
        
        # 获取当前用户
        current_user = get_current_user()
        
        # 创建知识库
        kb_storage = get_kb_storage()
        
        # 检查名称是否已存在
        existing = kb_storage.get_by_name(name)
        if existing:
            return bad_request(
                error_code="NAME_EXISTS",
                message=f"知识库名称 '{name}' 已存在"
            )
        
        kb_data = {
            'name': name,
            'description': data.get('description', ''),
            'category': data.get('category', 'general'),
            'status': 'active',
            'doc_count': 0,
            'created_by': current_user.get('user_id')
        }
        
        kb = kb_storage.create(kb_data)
        
        logger.info(f"Knowledge base created: {kb['id']} by {current_user.get('user_id')}")
        
        return success_response(
            data=kb,
            message="知识库创建成功",
            code=201
        )
        
    except Exception as e:
        logger.error(f"Create knowledge base error: {str(e)}")
        return internal_error(
            error_code="CREATE_KB_ERROR",
            message="创建知识库失败"
        )


@knowledge_bp.route('/<kb_id>', methods=['GET'])
@login_required
def get_knowledge_base(kb_id):
    """
    获取知识库详情
    
    路径参数:
        - kb_id: 知识库ID
    """
    try:
        kb_storage = get_kb_storage()
        kb = kb_storage.get(kb_id)
        
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        return success_response(data=kb)
        
    except Exception as e:
        logger.error(f"Get knowledge base error: {str(e)}")
        return internal_error(
            error_code="GET_KB_ERROR",
            message="获取知识库详情失败"
        )


@knowledge_bp.route('/<kb_id>', methods=['PUT'])
@login_required
def update_knowledge_base(kb_id):
    """
    更新知识库
    
    路径参数:
        - kb_id: 知识库ID
    
    请求体:
        {
            "name": "新名称",
            "description": "新描述",
            "category": "新分类",
            "status": "active/archived"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        kb_storage = get_kb_storage()
        
        # 检查知识库是否存在
        kb = kb_storage.get(kb_id)
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        # 构建更新数据
        updates = {}
        allowed_fields = ['name', 'description', 'category', 'status']
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]
        
        if not updates:
            return bad_request(
                error_code="NO_UPDATES",
                message="没有提供要更新的字段"
            )
        
        # 如果更新名称，检查是否与其他知识库冲突
        if 'name' in updates:
            existing = kb_storage.get_by_name(updates['name'])
            if existing and existing['id'] != kb_id:
                return bad_request(
                    error_code="NAME_EXISTS",
                    message=f"知识库名称 '{updates['name']}' 已存在"
                )
        
        updated_kb = kb_storage.update(kb_id, updates)
        
        logger.info(f"Knowledge base updated: {kb_id}")
        
        return success_response(
            data=updated_kb,
            message="知识库更新成功"
        )
        
    except Exception as e:
        logger.error(f"Update knowledge base error: {str(e)}")
        return internal_error(
            error_code="UPDATE_KB_ERROR",
            message="更新知识库失败"
        )


@knowledge_bp.route('/<kb_id>', methods=['DELETE'])
@login_required
def delete_knowledge_base(kb_id):
    """
    删除知识库（软删除）
    
    路径参数:
        - kb_id: 知识库ID
    """
    try:
        kb_storage = get_kb_storage()
        
        # 检查知识库是否存在
        kb = kb_storage.get(kb_id)
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        # 软删除
        success = kb_storage.delete(kb_id, soft_delete=True)
        
        if success:
            logger.info(f"Knowledge base deleted: {kb_id}")
            return success_response(
                data={"deleted": True},
                message="知识库删除成功"
            )
        else:
            return internal_error(
                error_code="DELETE_KB_ERROR",
                message="删除知识库失败"
            )
        
    except Exception as e:
        logger.error(f"Delete knowledge base error: {str(e)}")
        return internal_error(
            error_code="DELETE_KB_ERROR",
            message="删除知识库失败"
        )


# ==================== 文档管理接口 ====================

@knowledge_bp.route('/<kb_id>/docs', methods=['GET'])
@login_required
def list_documents(kb_id):
    """
    获取知识库下的文档列表
    
    路径参数:
        - kb_id: 知识库ID
    
    查询参数:
        - page: 页码
        - page_size: 每页条数
        - status: 按状态过滤
    """
    try:
        # 检查知识库是否存在
        kb_storage = get_kb_storage()
        kb = kb_storage.get(kb_id)
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        # 解析查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status')
        
        # 构建过滤条件
        filters = {'kb_id': kb_id}
        if status:
            filters['status'] = status
        
        # 查询数据
        doc_storage = get_doc_storage()
        result = doc_storage.list(
            filters=filters,
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
        logger.error(f"List documents error: {str(e)}")
        return internal_error(
            error_code="LIST_DOCS_ERROR",
            message="获取文档列表失败"
        )


@knowledge_bp.route('/<kb_id>/docs', methods=['POST'])
@login_required
def create_document(kb_id):
    """
    创建文档
    
    路径参数:
        - kb_id: 知识库ID
    
    请求体:
        {
            "title": "文档标题",
            "content": "文档内容",
            "category": "分类",
            "tags": ["标签1", "标签2"],
            "source": "来源",
            "status": "published/draft"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        # 必填字段校验
        title = data.get('title', '').strip()
        if not title:
            return bad_request(
                error_code="MISSING_TITLE",
                message="文档标题不能为空"
            )
        
        # 检查知识库是否存在
        kb_storage = get_kb_storage()
        kb = kb_storage.get(kb_id)
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        # 获取当前用户
        current_user = get_current_user()
        
        # 创建文档
        doc_storage = get_doc_storage()
        
        doc_data = {
            'kb_id': kb_id,
            'title': title,
            'content': data.get('content', ''),
            'category': data.get('category', 'general'),
            'tags': data.get('tags', []),
            'source': data.get('source', ''),
            'status': data.get('status', 'published'),
            'created_by': current_user.get('user_id')
        }
        
        doc = doc_storage.create(doc_data)
        
        # 更新知识库文档计数
        kb_storage.increment_doc_count(kb_id, 1)
        
        logger.info(f"Document created: {doc['id']} in KB {kb_id}")
        
        return success_response(
            data=doc,
            message="文档创建成功",
            code=201
        )
        
    except Exception as e:
        logger.error(f"Create document error: {str(e)}")
        return internal_error(
            error_code="CREATE_DOC_ERROR",
            message="创建文档失败"
        )


@knowledge_bp.route('/<kb_id>/docs/<doc_id>', methods=['PUT'])
@login_required
def update_document(kb_id, doc_id):
    """
    更新文档
    
    路径参数:
        - kb_id: 知识库ID
        - doc_id: 文档ID
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        # 检查知识库是否存在
        kb_storage = get_kb_storage()
        kb = kb_storage.get(kb_id)
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        # 检查文档是否存在
        doc_storage = get_doc_storage()
        doc = doc_storage.get(doc_id)
        if not doc or doc.get('kb_id') != kb_id:
            return not_found(
                error_code="DOC_NOT_FOUND",
                message="文档不存在"
            )
        
        # 构建更新数据
        updates = {}
        allowed_fields = ['title', 'content', 'category', 'tags', 'source', 'status']
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]
        
        if not updates:
            return bad_request(
                error_code="NO_UPDATES",
                message="没有提供要更新的字段"
            )
        
        updated_doc = doc_storage.update(doc_id, updates)
        
        logger.info(f"Document updated: {doc_id}")
        
        return success_response(
            data=updated_doc,
            message="文档更新成功"
        )
        
    except Exception as e:
        logger.error(f"Update document error: {str(e)}")
        return internal_error(
            error_code="UPDATE_DOC_ERROR",
            message="更新文档失败"
        )


@knowledge_bp.route('/<kb_id>/docs/<doc_id>', methods=['DELETE'])
@login_required
def delete_document(kb_id, doc_id):
    """
    删除文档
    
    路径参数:
        - kb_id: 知识库ID
        - doc_id: 文档ID
    """
    try:
        # 检查知识库是否存在
        kb_storage = get_kb_storage()
        kb = kb_storage.get(kb_id)
        if not kb:
            return not_found(
                error_code="KB_NOT_FOUND",
                message="知识库不存在"
            )
        
        # 检查文档是否存在
        doc_storage = get_doc_storage()
        doc = doc_storage.get(doc_id)
        if not doc or doc.get('kb_id') != kb_id:
            return not_found(
                error_code="DOC_NOT_FOUND",
                message="文档不存在"
            )
        
        # 软删除
        success = doc_storage.delete(doc_id, soft_delete=True)
        
        if success:
            # 更新知识库文档计数
            kb_storage.increment_doc_count(kb_id, -1)
            
            logger.info(f"Document deleted: {doc_id}")
            return success_response(
                data={"deleted": True},
                message="文档删除成功"
            )
        else:
            return internal_error(
                error_code="DELETE_DOC_ERROR",
                message="删除文档失败"
            )
        
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        return internal_error(
            error_code="DELETE_DOC_ERROR",
            message="删除文档失败"
        )


# ==================== 搜索接口 ====================

@knowledge_bp.route('/search', methods=['GET'])
@login_required
def search_documents():
    """
    跨知识库搜索文档
    
    查询参数:
        - q: 搜索关键词（必填）
        - kb_id: 可选，指定知识库ID
        - limit: 返回结果数量限制（默认20）
    """
    try:
        keyword = request.args.get('q', '').strip()
        kb_id = request.args.get('kb_id')
        limit = request.args.get('limit', 20, type=int)
        
        if not keyword:
            return bad_request(
                error_code="MISSING_KEYWORD",
                message="搜索关键词不能为空"
            )
        
        # 如果指定了知识库ID，检查是否存在
        if kb_id:
            kb_storage = get_kb_storage()
            kb = kb_storage.get(kb_id)
            if not kb:
                return not_found(
                    error_code="KB_NOT_FOUND",
                    message="知识库不存在"
                )
        
        # 搜索文档
        doc_storage = get_doc_storage()
        results = doc_storage.search_all(keyword, kb_id)
        
        # 限制返回数量
        if limit > 0:
            results = results[:limit]
        
        return success_response(
            data={
                "keyword": keyword,
                "total": len(results),
                "results": results
            },
            message="搜索完成"
        )
        
    except Exception as e:
        logger.error(f"Search documents error: {str(e)}")
        return internal_error(
            error_code="SEARCH_ERROR",
            message="搜索文档失败"
        )
