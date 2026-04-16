"""
培训管理API路由模块
提供培训相关的RESTful API接口
"""

from flask import Blueprint, request, current_app

from app.services.training_service import TrainingService
from app.storage.training_storage import TrainingStorage, TrainingRecordStorage
from app.services.llm_service import LLMService
from app.utils.response import (
    success_response, paginated_response,
    bad_request, not_found, internal_error
)

training_bp = Blueprint('training', __name__)


def get_training_service():
    """获取培训服务实例"""
    config = {
        'LLM_API_KEY': current_app.config.get('LLM_API_KEY', ''),
        'LLM_API_URL': current_app.config.get('LLM_API_URL', ''),
        'LLM_MODEL': current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_TIMEOUT': current_app.config.get('LLM_TIMEOUT', 30)
    }
    llm_service = LLMService(config)
    data_dir = current_app.config.get('DATA_DIR', './data')
    storage = TrainingStorage(data_dir)
    return TrainingService(llm_service, storage)


def get_training_storage():
    """获取培训存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return TrainingStorage(data_dir)


def get_training_record_storage():
    """获取培训记录存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return TrainingRecordStorage(data_dir)


@training_bp.route('/', methods=['GET'])
def list_trainings():
    """获取培训列表"""
    try:
        # 获取查询参数
        training_type = request.args.get('type')
        status = request.args.get('status')
        difficulty = request.args.get('difficulty')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤条件
        filters = {}
        if training_type:
            filters['type'] = training_type
        if status:
            filters['status'] = status
        if difficulty:
            filters['difficulty'] = difficulty
        
        # 限制分页大小
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        
        storage = get_training_storage()
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
        current_app.logger.error(f"List trainings error: {str(e)}")
        return internal_error(message="获取培训列表失败")


@training_bp.route('/', methods=['POST'])
def create_training():
    """创建培训"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        # 必填字段校验
        required_fields = ['title', 'type', 'category']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return bad_request(
                message=f"缺少必填字段: {', '.join(missing_fields)}"
            )
        
        # 字段值校验
        valid_types = ['course', 'exam', 'practice']
        valid_statuses = ['draft', 'published', 'archived']
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        
        training_type = data.get('type')
        if training_type not in valid_types:
            return bad_request(
                message=f"无效的类型，必须是: {', '.join(valid_types)}"
            )
        
        status = data.get('status', 'draft')
        if status not in valid_statuses:
            return bad_request(
                message=f"无效的状态，必须是: {', '.join(valid_statuses)}"
            )
        
        difficulty = data.get('difficulty', 'intermediate')
        if difficulty not in valid_difficulties:
            return bad_request(
                message=f"无效的难度，必须是: {', '.join(valid_difficulties)}"
            )
        
        duration = data.get('duration_minutes', 30)
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            return bad_request(message="时长必须是整数")
        
        storage = get_training_storage()
        
        record = {
            'title': data['title'],
            'description': data.get('description', ''),
            'type': training_type,
            'category': data['category'],
            'content': data.get('content', ''),
            'duration_minutes': duration,
            'status': status,
            'difficulty': difficulty,
            'created_by': data.get('created_by', 'system')
        }
        
        result = storage.create(record)
        
        return success_response(data=result, message="培训创建成功", code=201)
    
    except Exception as e:
        current_app.logger.error(f"Create training error: {str(e)}")
        return internal_error(message="创建培训失败")


@training_bp.route('/<training_id>', methods=['GET'])
def get_training(training_id):
    """获取培训详情"""
    try:
        storage = get_training_storage()
        training = storage.get(training_id)
        
        if not training:
            return not_found(message="培训不存在")
        
        return success_response(data=training)
    
    except Exception as e:
        current_app.logger.error(f"Get training error: {str(e)}")
        return internal_error(message="获取培训详情失败")


@training_bp.route('/<training_id>', methods=['PUT'])
def update_training(training_id):
    """更新培训"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        storage = get_training_storage()
        
        # 检查培训是否存在
        existing = storage.get(training_id)
        if not existing:
            return not_found(message="培训不存在")
        
        # 过滤可更新字段
        allowed_fields = [
            'title', 'description', 'type', 'category',
            'content', 'duration_minutes', 'status', 'difficulty'
        ]
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        # 字段值校验
        valid_types = ['course', 'exam', 'practice']
        valid_statuses = ['draft', 'published', 'archived']
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        
        if 'type' in updates and updates['type'] not in valid_types:
            return bad_request(message="无效的类型")
        
        if 'status' in updates and updates['status'] not in valid_statuses:
            return bad_request(message="无效的状态")
        
        if 'difficulty' in updates and updates['difficulty'] not in valid_difficulties:
            return bad_request(message="无效的难度")
        
        result = storage.update(training_id, updates)
        
        if result:
            return success_response(data=result, message="培训更新成功")
        else:
            return internal_error(message="更新培训失败")
    
    except Exception as e:
        current_app.logger.error(f"Update training error: {str(e)}")
        return internal_error(message="更新培训失败")


@training_bp.route('/<training_id>/enroll', methods=['POST'])
def enroll_training(training_id):
    """报名培训"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        
        if not user_id:
            return bad_request(message="缺少用户ID(user_id)")
        if not user_name:
            return bad_request(message="缺少用户姓名(user_name)")
        
        # 检查培训是否存在且已发布
        training_storage = get_training_storage()
        training = training_storage.get(training_id)
        if not training:
            return not_found(message="培训不存在")
        if training['status'] != 'published':
            return bad_request(message="该培训未发布，无法报名")
        
        record_storage = get_training_record_storage()
        
        try:
            result = record_storage.enroll(training_id, user_id, user_name)
            return success_response(data=result, message="报名成功", code=201)
        except ValueError as e:
            return bad_request(message=str(e))
    
    except Exception as e:
        current_app.logger.error(f"Enroll training error: {str(e)}")
        return internal_error(message="报名失败")


@training_bp.route('/generate', methods=['POST'])
def generate_training_content():
    """AI生成培训内容"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        topic = data.get('topic')
        if not topic:
            return bad_request(message="缺少培训主题(topic)")
        
        difficulty = data.get('difficulty', 'intermediate')
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        if difficulty not in valid_difficulties:
            return bad_request(
                message=f"无效的难度，必须是: {', '.join(valid_difficulties)}"
            )
        
        service = get_training_service()
        result = service.generate_content(topic, difficulty)
        
        return success_response(data=result, message="培训内容生成成功")
    
    except ValueError as e:
        return bad_request(message=str(e))
    except Exception as e:
        current_app.logger.error(f"Generate training content error: {str(e)}")
        return internal_error(message="生成培训内容失败")


@training_bp.route('/exam/generate', methods=['POST'])
def generate_exam():
    """AI生成考核试题"""
    try:
        data = request.get_json()
        if not data:
            return bad_request(message="请求体不能为空")
        
        topic = data.get('topic')
        if not topic:
            return bad_request(message="缺少考核主题(topic)")
        
        question_count = data.get('question_count', 10)
        try:
            question_count = int(question_count)
        except (ValueError, TypeError):
            return bad_request(message="题目数量必须是整数")
        
        if question_count < 5 or question_count > 50:
            return bad_request(message="题目数量必须在5-50之间")
        
        service = get_training_service()
        result = service.generate_exam(topic, question_count)
        
        return success_response(data=result, message="考核试题生成成功")
    
    except ValueError as e:
        return bad_request(message=str(e))
    except Exception as e:
        current_app.logger.error(f"Generate exam error: {str(e)}")
        return internal_error(message="生成考核试题失败")


@training_bp.route('/records', methods=['GET'])
def list_records():
    """获取培训记录列表"""
    try:
        # 获取查询参数
        training_id = request.args.get('training_id')
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建过滤条件
        filters = {}
        if training_id:
            filters['training_id'] = training_id
        if user_id:
            filters['user_id'] = user_id
        if status:
            filters['status'] = status
        
        # 限制分页大小
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        
        storage = get_training_record_storage()
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
        current_app.logger.error(f"List training records error: {str(e)}")
        return internal_error(message="获取培训记录列表失败")


@training_bp.route('/records/<record_id>/start', methods=['POST'])
def start_training(record_id):
    """开始培训"""
    try:
        storage = get_training_record_storage()
        
        # 检查记录是否存在
        existing = storage.get(record_id)
        if not existing:
            return not_found(message="培训记录不存在")
        
        # 检查状态
        if existing['status'] not in ['enrolled']:
            return bad_request(message="当前状态无法开始培训")
        
        result = storage.start_training(record_id)
        
        if result:
            return success_response(data=result, message="培训已开始")
        else:
            return internal_error(message="开始培训失败")
    
    except Exception as e:
        current_app.logger.error(f"Start training error: {str(e)}")
        return internal_error(message="开始培训失败")


@training_bp.route('/records/<record_id>/complete', methods=['POST'])
def complete_training(record_id):
    """完成培训"""
    try:
        data = request.get_json() or {}
        score = data.get('score')
        
        if score is not None:
            try:
                score = int(score)
            except (ValueError, TypeError):
                return bad_request(message="分数必须是整数")
        
        storage = get_training_record_storage()
        
        # 检查记录是否存在
        existing = storage.get(record_id)
        if not existing:
            return not_found(message="培训记录不存在")
        
        # 检查状态
        if existing['status'] not in ['enrolled', 'in_progress']:
            return bad_request(message="当前状态无法完成培训")
        
        result = storage.complete_training(record_id, score)
        
        if result:
            return success_response(data=result, message="培训已完成")
        else:
            return internal_error(message="完成培训失败")
    
    except Exception as e:
        current_app.logger.error(f"Complete training error: {str(e)}")
        return internal_error(message="完成培训失败")


@training_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取培训统计数据"""
    try:
        training_id = request.args.get('training_id')
        
        # 培训统计
        training_storage = get_training_storage()
        training_stats = training_storage.get_statistics()
        
        # 培训记录统计
        record_storage = get_training_record_storage()
        record_stats = record_storage.get_statistics(training_id)
        
        return success_response(data={
            'training_stats': training_stats,
            'record_stats': record_stats
        })
    
    except Exception as e:
        current_app.logger.error(f"Get training statistics error: {str(e)}")
        return internal_error(message="获取统计数据失败")
