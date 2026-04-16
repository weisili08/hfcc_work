"""
智能问答API路由模块
提供AI问答、会话管理、反馈等功能
"""

import logging
from flask import Blueprint, request, current_app

from app.utils.response import (
    success_response, bad_request, not_found, 
    internal_error, paginated_response
)
from app.utils.auth import login_required, get_current_user
from app.services.qa_service import QAService
from app.services.llm_service import LLMService
from app.storage.qa_session_storage import QASessionStorage
from app.storage.qa_record_storage import QARecordStorage
from app.storage.kb_doc_storage import KBDocumentStorage


logger = logging.getLogger(__name__)

# 创建蓝图
qa_bp = Blueprint('qa', __name__)


def get_qa_service():
    """获取问答服务实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    
    # 初始化LLM服务
    llm_config = {
        'LLM_API_KEY': current_app.config.get('LLM_API_KEY', ''),
        'LLM_API_URL': current_app.config.get('LLM_API_URL', ''),
        'LLM_MODEL': current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_TIMEOUT': current_app.config.get('LLM_TIMEOUT', 30),
        'LLM_BACKUP_API_KEY': current_app.config.get('LLM_BACKUP_API_KEY', ''),
        'LLM_BACKUP_API_URL': current_app.config.get('LLM_BACKUP_API_URL', ''),
        'LLM_BACKUP_MODEL': current_app.config.get('LLM_BACKUP_MODEL', '')
    }
    llm_service = LLMService(llm_config)
    
    # 初始化文档存储
    kb_doc_storage = KBDocumentStorage(data_dir)
    
    # 初始化问答服务
    return QAService(llm_service, kb_doc_storage)


def get_session_storage():
    """获取会话存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return QASessionStorage(data_dir)


def get_record_storage():
    """获取记录存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return QARecordStorage(data_dir)


# ==================== 问答接口 ====================

@qa_bp.route('/ask', methods=['POST'])
@login_required
def ask_question():
    """
    发送问题获取AI回答
    
    请求体:
        {
            "query": "用户问题",
            "session_id": "可选，会话ID"
        }
    
    响应:
        {
            "data": {
                "answer": "AI回答",
                "sources": [...],
                "confidence": 0.85,
                "answer_source": "knowledge",
                "session_id": "会话ID",
                "response_time_ms": 1200
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        query = data.get('query', '').strip()
        session_id = data.get('session_id')
        
        # 参数校验
        if not query:
            return bad_request(
                error_code="MISSING_QUERY",
                message="问题内容不能为空"
            )
        
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 初始化存储
        session_storage = get_session_storage()
        record_storage = get_record_storage()
        
        # 如果没有session_id，创建新会话
        if not session_id:
            session_title = session_storage.generate_title(query)
            session = session_storage.create({
                'title': session_title,
                'user_id': user_id,
                'message_count': 0,
                'status': 'active'
            })
            session_id = session['id']
            logger.info(f"New QA session created: {session_id}")
        else:
            # 验证会话是否存在且属于当前用户
            session = session_storage.get(session_id)
            if not session:
                return not_found(
                    error_code="SESSION_NOT_FOUND",
                    message="会话不存在"
                )
            if session.get('user_id') != user_id:
                return bad_request(
                    error_code="SESSION_ACCESS_DENIED",
                    message="无权访问该会话"
                )
        
        # 调用问答服务
        qa_service = get_qa_service()
        result = qa_service.ask(query, session_id=session_id)
        
        # 保存问答记录
        record_data = {
            'session_id': session_id,
            'query': query,
            'answer': result['answer'],
            'sources': result['sources'],
            'confidence': result['confidence'],
            'answer_source': result['answer_source'],
            'response_time_ms': result['response_time_ms']
        }
        record = record_storage.create(record_data)
        
        # 更新会话消息计数
        session_storage.increment_message_count(session_id, 1)
        
        # 添加记录ID到结果
        result['record_id'] = record['id']
        
        logger.info(f"QA completed: session={session_id}, record={record['id']}")
        
        return success_response(
            data=result,
            message="回答生成成功"
        )
        
    except Exception as e:
        logger.error(f"Ask question error: {str(e)}")
        return internal_error(
            error_code="QA_ERROR",
            message="问答服务异常"
        )


# ==================== 会话管理接口 ====================

@qa_bp.route('/sessions', methods=['GET'])
@login_required
def list_sessions():
    """
    获取当前用户的会话列表
    
    查询参数:
        - page: 页码（默认1）
        - page_size: 每页条数（默认20）
        - status: 按状态过滤
    """
    try:
        # 解析查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status')
        
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 构建过滤条件
        filters = {'user_id': user_id}
        if status:
            filters['status'] = status
        
        # 查询数据
        session_storage = get_session_storage()
        result = session_storage.list(
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
        logger.error(f"List sessions error: {str(e)}")
        return internal_error(
            error_code="LIST_SESSIONS_ERROR",
            message="获取会话列表失败"
        )


@qa_bp.route('/sessions/<session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """
    获取会话详情（含历史消息）
    
    路径参数:
        - session_id: 会话ID
    """
    try:
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 获取会话
        session_storage = get_session_storage()
        session = session_storage.get(session_id)
        
        if not session:
            return not_found(
                error_code="SESSION_NOT_FOUND",
                message="会话不存在"
            )
        
        # 验证会话所有权
        if session.get('user_id') != user_id:
            return bad_request(
                error_code="SESSION_ACCESS_DENIED",
                message="无权访问该会话"
            )
        
        # 获取会话历史消息
        record_storage = get_record_storage()
        history = record_storage.get_session_history(session_id)
        
        return success_response(
            data={
                'session': session,
                'messages': history
            },
            message="获取会话详情成功"
        )
        
    except Exception as e:
        logger.error(f"Get session error: {str(e)}")
        return internal_error(
            error_code="GET_SESSION_ERROR",
            message="获取会话详情失败"
        )


@qa_bp.route('/sessions/<session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """
    删除会话
    
    路径参数:
        - session_id: 会话ID
    """
    try:
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 获取会话
        session_storage = get_session_storage()
        session = session_storage.get(session_id)
        
        if not session:
            return not_found(
                error_code="SESSION_NOT_FOUND",
                message="会话不存在"
            )
        
        # 验证会话所有权
        if session.get('user_id') != user_id:
            return bad_request(
                error_code="SESSION_ACCESS_DENIED",
                message="无权删除该会话"
            )
        
        # 软删除会话
        success = session_storage.delete(session_id, soft_delete=True)
        
        if success:
            logger.info(f"Session deleted: {session_id}")
            return success_response(
                data={"deleted": True},
                message="会话删除成功"
            )
        else:
            return internal_error(
                error_code="DELETE_SESSION_ERROR",
                message="删除会话失败"
            )
        
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}")
        return internal_error(
            error_code="DELETE_SESSION_ERROR",
            message="删除会话失败"
        )


# ==================== 反馈接口 ====================

@qa_bp.route('/feedback', methods=['POST'])
@login_required
def add_feedback():
    """
    添加问答反馈
    
    请求体:
        {
            "record_id": "记录ID",
            "rating": 5,           // 评分 1-5
            "comment": "可选评论"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        record_id = data.get('record_id')
        rating = data.get('rating')
        comment = data.get('comment')
        
        # 参数校验
        if not record_id:
            return bad_request(
                error_code="MISSING_RECORD_ID",
                message="记录ID不能为空"
            )
        
        if rating is None:
            return bad_request(
                error_code="MISSING_RATING",
                message="评分不能为空"
            )
        
        # 评分范围校验
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return bad_request(
                error_code="INVALID_RATING",
                message="评分必须在1-5之间"
            )
        
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 获取记录
        record_storage = get_record_storage()
        
        # 验证记录是否存在
        # 注意：这里简化处理，实际应该验证记录所属会话是否属于当前用户
        record = record_storage.get(record_id)
        if not record:
            return not_found(
                error_code="RECORD_NOT_FOUND",
                message="问答记录不存在"
            )
        
        # 添加反馈
        updated_record = record_storage.add_feedback(record_id, rating, comment)
        
        if updated_record:
            logger.info(f"Feedback added: record={record_id}, rating={rating}")
            return success_response(
                data={
                    'record_id': record_id,
                    'rating': rating,
                    'comment': comment
                },
                message="反馈提交成功"
            )
        else:
            return internal_error(
                error_code="ADD_FEEDBACK_ERROR",
                message="添加反馈失败"
            )
        
    except Exception as e:
        logger.error(f"Add feedback error: {str(e)}")
        return internal_error(
            error_code="ADD_FEEDBACK_ERROR",
            message="添加反馈失败"
        )


# ==================== 统计接口 ====================

@qa_bp.route('/sessions/<session_id>/statistics', methods=['GET'])
@login_required
def get_session_statistics(session_id):
    """
    获取会话统计信息
    
    路径参数:
        - session_id: 会话ID
    """
    try:
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 获取会话
        session_storage = get_session_storage()
        session = session_storage.get(session_id)
        
        if not session:
            return not_found(
                error_code="SESSION_NOT_FOUND",
                message="会话不存在"
            )
        
        # 验证会话所有权
        if session.get('user_id') != user_id:
            return bad_request(
                error_code="SESSION_ACCESS_DENIED",
                message="无权访问该会话"
            )
        
        # 获取统计信息
        record_storage = get_record_storage()
        statistics = record_storage.get_statistics(session_id)
        
        return success_response(
            data=statistics,
            message="获取统计信息成功"
        )
        
    except Exception as e:
        logger.error(f"Get statistics error: {str(e)}")
        return internal_error(
            error_code="GET_STATISTICS_ERROR",
            message="获取统计信息失败"
        )
