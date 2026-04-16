"""
问答记录存储模块
提供问答记录的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class QARecordStorage(BaseStorage):
    """
    问答记录存储类
    
    字段：
    - id: 唯一标识
    - session_id: 所属会话ID
    - query: 用户问题
    - answer: AI回答
    - sources: 知识来源列表
    - confidence: 置信度 (0-1)
    - answer_source: 回答来源 (llm/knowledge/fallback)
    - response_time_ms: 响应时间（毫秒）
    - feedback_rating: 用户评分（可选）
    - feedback_comment: 用户评论（可选）
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化问答记录存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'qa_records.json')
    
    def _get_id_prefix(self) -> str:
        """获取记录ID前缀"""
        return 'rec'
    
    def list_by_session(self, session_id: str, **kwargs) -> dict:
        """
        列出指定会话下的问答记录
        
        Args:
            session_id: 会话ID
            **kwargs: 其他过滤条件
            
        Returns:
            dict: 分页结果
        """
        filters = kwargs.get('filters', {})
        filters['session_id'] = session_id
        kwargs['filters'] = filters
        kwargs['sort_by'] = kwargs.get('sort_by', 'created_at')
        kwargs['sort_order'] = kwargs.get('sort_order', 'asc')
        return self.list(**kwargs)
    
    def get_session_history(self, session_id: str, limit: int = None) -> list:
        """
        获取会话历史消息
        
        Args:
            session_id: 会话ID
            limit: 限制返回数量
            
        Returns:
            list: 问答记录列表，按时间升序排列
        """
        result = self.list_by_session(
            session_id,
            page=1,
            page_size=limit or 100,
            sort_by='created_at',
            sort_order='asc'
        )
        
        return result['items']
    
    def add_feedback(self, record_id: str, rating: int, comment: str = None) -> dict:
        """
        添加用户反馈
        
        Args:
            record_id: 记录ID
            rating: 评分（1-5）
            comment: 评论（可选）
            
        Returns:
            dict | None: 更新后的记录
        """
        updates = {'feedback_rating': rating}
        if comment is not None:
            updates['feedback_comment'] = comment
        
        return self.update(record_id, updates)
    
    def get_statistics(self, session_id: str = None) -> dict:
        """
        获取问答统计信息
        
        Args:
            session_id: 可选，指定会话ID
            
        Returns:
            dict: 统计信息
        """
        data = self._load()
        
        # 过滤数据
        records = []
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            if session_id and item.get('session_id') != session_id:
                continue
            records.append(item)
        
        if not records:
            return {
                'total': 0,
                'avg_confidence': 0,
                'avg_response_time_ms': 0,
                'source_distribution': {},
                'feedback_avg': 0
            }
        
        # 计算统计
        total = len(records)
        
        # 置信度
        confidences = [r.get('confidence', 0) for r in records if r.get('confidence') is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # 响应时间
        response_times = [r.get('response_time_ms', 0) for r in records if r.get('response_time_ms') is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 回答来源分布
        source_distribution = {}
        for r in records:
            source = r.get('answer_source', 'unknown')
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # 反馈评分
        feedbacks = [r.get('feedback_rating') for r in records if r.get('feedback_rating') is not None]
        feedback_avg = sum(feedbacks) / len(feedbacks) if feedbacks else 0
        
        return {
            'total': total,
            'avg_confidence': round(avg_confidence, 2),
            'avg_response_time_ms': round(avg_response_time, 2),
            'source_distribution': source_distribution,
            'feedback_avg': round(feedback_avg, 2) if feedbacks else None
        }
