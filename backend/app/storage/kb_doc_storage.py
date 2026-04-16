"""
知识库文档存储模块
提供知识库文档的CRUD操作和搜索功能
"""

from app.storage.base_storage import BaseStorage


class KBDocumentStorage(BaseStorage):
    """
    知识库文档存储类
    
    字段：
    - id: 唯一标识
    - kb_id: 所属知识库ID
    - title: 文档标题
    - content: 文档内容
    - category: 分类
    - tags: 标签列表
    - source: 来源
    - status: 状态 (published/draft/archived)
    - created_by: 创建者用户ID
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化知识库文档存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'kb_documents.json')
    
    def _get_id_prefix(self) -> str:
        """获取文档ID前缀"""
        return 'doc'
    
    def list_by_kb(self, kb_id: str, **kwargs) -> dict:
        """
        列出指定知识库下的文档
        
        Args:
            kb_id: 知识库ID
            **kwargs: 其他过滤条件
            
        Returns:
            dict: 分页结果
        """
        filters = kwargs.get('filters', {})
        filters['kb_id'] = kb_id
        kwargs['filters'] = filters
        return self.list(**kwargs)
    
    def search_docs(self, kb_id: str, keyword: str) -> list:
        """
        在指定知识库中搜索文档
        
        在标题和内容中搜索关键词
        
        Args:
            kb_id: 知识库ID
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的文档列表
        """
        if not keyword:
            return []
        
        data = self._load()
        keyword_lower = keyword.lower()
        results = []
        
        for item in data:
            # 检查知识库ID匹配
            if item.get('kb_id') != kb_id:
                continue
            
            # 跳过已删除记录
            if item.get('deleted_at') is not None:
                continue
            
            # 在标题和内容中搜索
            title = item.get('title', '')
            content = item.get('content', '')
            
            if (keyword_lower in title.lower() or 
                keyword_lower in content.lower()):
                results.append(item.copy())
        
        return results
    
    def search_all(self, keyword: str, kb_id: str = None) -> list:
        """
        跨知识库搜索文档
        
        Args:
            keyword: 搜索关键词
            kb_id: 可选，指定知识库ID
            
        Returns:
            list: 匹配的文档列表
        """
        if not keyword:
            return []
        
        data = self._load()
        keyword_lower = keyword.lower()
        results = []
        
        for item in data:
            # 跳过已删除记录
            if item.get('deleted_at') is not None:
                continue
            
            # 如果指定了知识库ID，进行过滤
            if kb_id and item.get('kb_id') != kb_id:
                continue
            
            # 在标题、内容、标签中搜索
            title = item.get('title', '')
            content = item.get('content', '')
            tags = item.get('tags', [])
            
            # 将标签列表转为字符串搜索
            tags_str = ' '.join(tags) if tags else ''
            
            if (keyword_lower in title.lower() or 
                keyword_lower in content.lower() or
                keyword_lower in tags_str.lower()):
                results.append(item.copy())
        
        return results
    
    def get_by_status(self, kb_id: str, status: str) -> list:
        """
        获取指定状态的文档
        
        Args:
            kb_id: 知识库ID
            status: 状态 (published/draft/archived)
            
        Returns:
            list: 文档列表
        """
        data = self._load()
        results = []
        
        for item in data:
            if (item.get('kb_id') == kb_id and 
                item.get('status') == status and
                item.get('deleted_at') is None):
                results.append(item.copy())
        
        return results
    
    def publish(self, doc_id: str) -> dict:
        """
        发布文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            dict | None: 更新后的文档记录
        """
        return self.update(doc_id, {'status': 'published'})
    
    def archive(self, doc_id: str) -> dict:
        """
        归档文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            dict | None: 更新后的文档记录
        """
        return self.update(doc_id, {'status': 'archived'})
    
    def count_by_kb(self, kb_id: str, status: str = None) -> int:
        """
        统计知识库下的文档数量
        
        Args:
            kb_id: 知识库ID
            status: 可选，指定状态
            
        Returns:
            int: 文档数量
        """
        filters = {'kb_id': kb_id}
        if status:
            filters['status'] = status
        
        return self.count(filters=filters)
