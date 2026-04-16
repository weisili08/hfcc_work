"""
知识库存储模块
提供知识库的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class KnowledgeBaseStorage(BaseStorage):
    """
    知识库存储类
    
    字段：
    - id: 唯一标识
    - name: 知识库名称
    - description: 知识库描述
    - category: 分类
    - status: 状态 (active/archived)
    - doc_count: 文档数量
    - created_by: 创建者用户ID
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化知识库存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'knowledge_bases.json')
    
    def _get_id_prefix(self) -> str:
        """获取知识库ID前缀"""
        return 'kb'
    
    def get_by_name(self, name: str) -> dict:
        """
        按名称获取知识库
        
        Args:
            name: 知识库名称
            
        Returns:
            dict | None: 知识库记录，不存在返回None
        """
        data = self._load()
        for item in data:
            if item.get('name') == name and item.get('deleted_at') is None:
                return item.copy()
        return None
    
    def list_by_category(self, category: str, **kwargs) -> dict:
        """
        按分类列出知识库
        
        Args:
            category: 分类名称
            **kwargs: 其他过滤条件
            
        Returns:
            dict: 分页结果
        """
        filters = kwargs.get('filters', {})
        filters['category'] = category
        kwargs['filters'] = filters
        return self.list(**kwargs)
    
    def increment_doc_count(self, kb_id: str, delta: int = 1) -> dict:
        """
        增加/减少文档计数
        
        Args:
            kb_id: 知识库ID
            delta: 变化量（正数增加，负数减少）
            
        Returns:
            dict | None: 更新后的知识库记录
        """
        kb = self.get(kb_id)
        if not kb:
            return None
        
        current_count = kb.get('doc_count', 0)
        new_count = max(0, current_count + delta)
        
        return self.update(kb_id, {'doc_count': new_count})
    
    def archive(self, kb_id: str) -> dict:
        """
        归档知识库
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            dict | None: 更新后的知识库记录
        """
        return self.update(kb_id, {'status': 'archived'})
    
    def activate(self, kb_id: str) -> dict:
        """
        激活知识库
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            dict | None: 更新后的知识库记录
        """
        return self.update(kb_id, {'status': 'active'})
