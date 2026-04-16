"""
问答会话存储模块
提供问答会话的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class QASessionStorage(BaseStorage):
    """
    问答会话存储类
    
    字段：
    - id: 唯一标识
    - title: 会话标题
    - user_id: 创建者用户ID
    - message_count: 消息数量
    - status: 状态 (active/archived)
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化问答会话存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'qa_sessions.json')
    
    def _get_id_prefix(self) -> str:
        """获取会话ID前缀"""
        return 'qa'
    
    def list_by_user(self, user_id: str, **kwargs) -> dict:
        """
        列出指定用户的会话
        
        Args:
            user_id: 用户ID
            **kwargs: 其他过滤条件
            
        Returns:
            dict: 分页结果
        """
        filters = kwargs.get('filters', {})
        filters['user_id'] = user_id
        kwargs['filters'] = filters
        return self.list(**kwargs)
    
    def increment_message_count(self, session_id: str, delta: int = 1) -> dict:
        """
        增加消息计数
        
        Args:
            session_id: 会话ID
            delta: 变化量
            
        Returns:
            dict | None: 更新后的会话记录
        """
        session = self.get(session_id)
        if not session:
            return None
        
        current_count = session.get('message_count', 0)
        new_count = max(0, current_count + delta)
        
        return self.update(session_id, {'message_count': new_count})
    
    def archive(self, session_id: str) -> dict:
        """
        归档会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            dict | None: 更新后的会话记录
        """
        return self.update(session_id, {'status': 'archived'})
    
    def generate_title(self, query: str) -> str:
        """
        根据查询生成会话标题
        
        取查询的前20个字符作为标题
        
        Args:
            query: 用户查询
            
        Returns:
            str: 生成的标题
        """
        if not query:
            return "新会话"
        
        # 移除多余空白
        query = query.strip()
        
        # 取前20个字符
        if len(query) <= 20:
            return query
        else:
            return query[:20] + "..."
