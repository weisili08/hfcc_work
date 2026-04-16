"""
培训管理存储模块
提供培训课程和培训记录的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class TrainingStorage(BaseStorage):
    """
    培训课程存储类
    
    字段：
    - id: 唯一标识
    - title: 培训标题
    - description: 培训描述
    - type: 类型 (course/exam/practice)
    - category: 分类
    - content: 培训内容
    - duration_minutes: 预计时长（分钟）
    - status: 状态 (draft/published/archived)
    - difficulty: 难度 (beginner/intermediate/advanced)
    - created_by: 创建人
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化培训存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'trainings.json')
    
    def get_by_type(self, training_type: str) -> list:
        """
        按类型查询培训
        
        Args:
            training_type: 培训类型
        
        Returns:
            list: 符合条件的培训列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('type') == training_type and item.get('deleted_at') is None
        ]
    
    def get_by_status(self, status: str) -> list:
        """
        按状态查询培训
        
        Args:
            status: 状态
        
        Returns:
            list: 符合条件的培训列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('status') == status and item.get('deleted_at') is None
        ]
    
    def get_by_difficulty(self, difficulty: str) -> list:
        """
        按难度查询培训
        
        Args:
            difficulty: 难度
        
        Returns:
            list: 符合条件的培训列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('difficulty') == difficulty and item.get('deleted_at') is None
        ]
    
    def publish(self, training_id: str) -> dict:
        """
        发布培训
        
        Args:
            training_id: 培训ID
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(training_id, {'status': 'published'})
    
    def archive(self, training_id: str) -> dict:
        """
        归档培训
        
        Args:
            training_id: 培训ID
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(training_id, {'status': 'archived'})
    
    def get_statistics(self) -> dict:
        """
        获取培训统计数据
        
        Returns:
            dict: 统计数据
        """
        data = self._load()
        records = [item for item in data if item.get('deleted_at') is None]
        
        total = len(records)
        
        # 按类型统计
        type_counts = {}
        for item in records:
            training_type = item.get('type', 'unknown')
            type_counts[training_type] = type_counts.get(training_type, 0) + 1
        
        # 按状态统计
        status_counts = {}
        for item in records:
            status = item.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 按难度统计
        difficulty_counts = {}
        for item in records:
            difficulty = item.get('difficulty', 'unknown')
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        return {
            'total': total,
            'by_type': type_counts,
            'by_status': status_counts,
            'by_difficulty': difficulty_counts,
            'published_count': status_counts.get('published', 0),
            'draft_count': status_counts.get('draft', 0),
            'archived_count': status_counts.get('archived', 0)
        }


class TrainingRecordStorage(BaseStorage):
    """
    培训记录存储类
    
    字段：
    - id: 唯一标识
    - training_id: 培训课程ID
    - user_id: 用户ID
    - user_name: 用户姓名
    - status: 状态 (enrolled/in_progress/completed/failed)
    - score: 得分
    - start_time: 开始时间
    - complete_time: 完成时间
    - created_at: 创建时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化培训记录存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'training_records.json')
    
    def get_by_training(self, training_id: str) -> list:
        """
        按培训ID查询记录
        
        Args:
            training_id: 培训ID
        
        Returns:
            list: 符合条件的记录列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('training_id') == training_id and item.get('deleted_at') is None
        ]
    
    def get_by_user(self, user_id: str) -> list:
        """
        按用户ID查询记录
        
        Args:
            user_id: 用户ID
        
        Returns:
            list: 符合条件的记录列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('user_id') == user_id and item.get('deleted_at') is None
        ]
    
    def get_by_user_and_training(self, user_id: str, training_id: str) -> dict:
        """
        按用户ID和培训ID查询记录
        
        Args:
            user_id: 用户ID
            training_id: 培训ID
        
        Returns:
            dict | None: 记录
        """
        data = self._load()
        for item in data:
            if (item.get('user_id') == user_id and 
                item.get('training_id') == training_id and 
                item.get('deleted_at') is None):
                return item.copy()
        return None
    
    def enroll(self, training_id: str, user_id: str, user_name: str) -> dict:
        """
        报名培训
        
        Args:
            training_id: 培训ID
            user_id: 用户ID
            user_name: 用户姓名
        
        Returns:
            dict: 创建的记录
        """
        # 检查是否已报名
        existing = self.get_by_user_and_training(user_id, training_id)
        if existing:
            raise ValueError("用户已报名该培训")
        
        record = {
            'training_id': training_id,
            'user_id': user_id,
            'user_name': user_name,
            'status': 'enrolled',
            'score': None,
            'start_time': None,
            'complete_time': None
        }
        
        return self.create(record)
    
    def start_training(self, record_id: str) -> dict:
        """
        开始培训
        
        Args:
            record_id: 记录ID
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {
            'status': 'in_progress',
            'start_time': self._get_timestamp()
        }
        return self.update(record_id, updates)
    
    def complete_training(self, record_id: str, score: int = None) -> dict:
        """
        完成培训
        
        Args:
            record_id: 记录ID
            score: 得分（可选）
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {
            'status': 'completed',
            'complete_time': self._get_timestamp()
        }
        if score is not None:
            updates['score'] = score
        
        return self.update(record_id, updates)
    
    def fail_training(self, record_id: str) -> dict:
        """
        标记培训未通过
        
        Args:
            record_id: 记录ID
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {
            'status': 'failed',
            'complete_time': self._get_timestamp()
        }
        return self.update(record_id, updates)
    
    def get_statistics(self, training_id: str = None) -> dict:
        """
        获取培训记录统计
        
        Args:
            training_id: 培训ID（可选，不传则统计全部）
        
        Returns:
            dict: 统计数据
        """
        data = self._load()
        records = [item for item in data if item.get('deleted_at') is None]
        
        if training_id:
            records = [item for item in records if item.get('training_id') == training_id]
        
        total = len(records)
        
        # 按状态统计
        status_counts = {}
        for item in records:
            status = item.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 计算完成率
        completed = status_counts.get('completed', 0)
        completion_rate = round(completed / total * 100, 2) if total > 0 else 0
        
        # 平均分统计
        completed_records = [item for item in records if item.get('status') == 'completed' and item.get('score') is not None]
        avg_score = 0
        if completed_records:
            avg_score = sum(item.get('score', 0) for item in completed_records) / len(completed_records)
        
        return {
            'total': total,
            'by_status': status_counts,
            'completion_rate': completion_rate,
            'average_score': round(avg_score, 2),
            'completed_count': completed,
            'in_progress_count': status_counts.get('in_progress', 0),
            'enrolled_count': status_counts.get('enrolled', 0)
        }
