"""
投教内容存储模块
提供投教内容的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class EducationContentStorage(BaseStorage):
    """
    投教内容存储类
    
    存储字段：
    - id: 内容ID (edu_{uuid})
    - title: 标题
    - category: 分类 (fund_basics/risk_management/market_knowledge/regulation)
    - target_audience: 目标受众 (beginner/intermediate/advanced)
    - content: 内容正文
    - format: 格式 (article/qa/infographic)
    - tags: 标签列表
    - status: 状态 (draft/review/published/archived)
    - view_count: 浏览次数
    - like_count: 点赞次数
    - created_by: 创建人
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化投教内容存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'education_contents.json')
    
    def create_content(self, content_data: dict) -> dict:
        """
        创建投教内容
        
        Args:
            content_data: 内容数据字典
            
        Returns:
            dict: 创建后的完整记录
        """
        # 设置默认值
        if 'status' not in content_data:
            content_data['status'] = 'draft'
        if 'view_count' not in content_data:
            content_data['view_count'] = 0
        if 'like_count' not in content_data:
            content_data['like_count'] = 0
        if 'tags' not in content_data:
            content_data['tags'] = []
        
        return self.create(content_data)
    
    def get_content_by_id(self, content_id: str) -> dict:
        """
        按ID获取投教内容
        
        Args:
            content_id: 内容ID
            
        Returns:
            dict: 内容记录，不存在返回None
        """
        return self.get(content_id)
    
    def update_content(self, content_id: str, updates: dict) -> dict:
        """
        更新投教内容
        
        Args:
            content_id: 内容ID
            updates: 更新的字段
            
        Returns:
            dict: 更新后的记录
        """
        return self.update(content_id, updates)
    
    def delete_content(self, content_id: str, soft_delete: bool = True) -> bool:
        """
        删除投教内容
        
        Args:
            content_id: 内容ID
            soft_delete: 是否软删除
            
        Returns:
            bool: 删除是否成功
        """
        return self.delete(content_id, soft_delete)
    
    def list_contents(self, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        """
        列表查询投教内容
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def search_contents(self, keyword: str) -> list:
        """
        搜索投教内容
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的内容列表
        """
        return self.search(keyword, fields=['title', 'content', 'tags'])
    
    def increment_view_count(self, content_id: str) -> dict:
        """
        增加浏览次数
        
        Args:
            content_id: 内容ID
            
        Returns:
            dict: 更新后的记录
        """
        content = self.get(content_id)
        if content:
            new_count = content.get('view_count', 0) + 1
            return self.update(content_id, {'view_count': new_count})
        return None
    
    def increment_like_count(self, content_id: str) -> dict:
        """
        增加点赞次数
        
        Args:
            content_id: 内容ID
            
        Returns:
            dict: 更新后的记录
        """
        content = self.get(content_id)
        if content:
            new_count = content.get('like_count', 0) + 1
            return self.update(content_id, {'like_count': new_count})
        return None
    
    def get_contents_by_category(self, category: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按分类获取内容
        
        Args:
            category: 分类
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'category': category},
            page=page,
            page_size=page_size
        )
    
    def get_contents_by_audience(self, target_audience: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按目标受众获取内容
        
        Args:
            target_audience: 目标受众
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'target_audience': target_audience},
            page=page,
            page_size=page_size
        )
    
    def get_published_contents(self, page: int = 1, page_size: int = 20) -> dict:
        """
        获取已发布的内容
        
        Args:
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'status': 'published'},
            page=page,
            page_size=page_size
        )
