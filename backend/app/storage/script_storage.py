"""
话术存储模块
提供话术记录的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class ScriptStorage(BaseStorage):
    """
    话术存储类
    
    字段：
    - id: 唯一标识
    - scenario: 场景
    - context: 上下文信息
    - style: 风格
    - content: 话术内容
    - rating: 评分（1-5）
    - created_by: 创建人
    - created_at: 创建时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化话术存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'scripts.json')
    
    def get_by_scenario(self, scenario: str) -> list:
        """
        按场景查询话术
        
        Args:
            scenario: 场景名称
        
        Returns:
            list: 符合条件的话术列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('scenario') == scenario and item.get('deleted_at') is None
        ]
    
    def get_by_rating(self, min_rating: int = 4) -> list:
        """
        按评分查询话术
        
        Args:
            min_rating: 最低评分
        
        Returns:
            list: 符合条件的话术列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('rating', 0) >= min_rating and item.get('deleted_at') is None
        ]
    
    def update_rating(self, script_id: str, rating: int, comment: str = '') -> dict:
        """
        更新话术评分
        
        Args:
            script_id: 话术ID
            rating: 评分（1-5）
            comment: 评价备注
        
        Returns:
            dict | None: 更新后的记录
        """
        if not 1 <= rating <= 5:
            raise ValueError("评分必须在1-5之间")
        
        updates = {
            'rating': rating,
            'rating_comment': comment
        }
        
        return self.update(script_id, updates)
    
    def get_statistics(self) -> dict:
        """
        获取话术统计数据
        
        Returns:
            dict: 统计数据
        """
        data = self._load()
        records = [item for item in data if item.get('deleted_at') is None]
        
        total = len(records)
        
        # 按场景统计
        scenario_counts = {}
        for item in records:
            scenario = item.get('scenario', 'unknown')
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
        
        # 按风格统计
        style_counts = {}
        for item in records:
            style = item.get('style', 'unknown')
            style_counts[style] = style_counts.get(style, 0) + 1
        
        # 评分统计
        rated_records = [item for item in records if item.get('rating') is not None]
        avg_rating = 0
        if rated_records:
            avg_rating = sum(item.get('rating', 0) for item in rated_records) / len(rated_records)
        
        rating_distribution = {}
        for item in rated_records:
            rating = item.get('rating')
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        return {
            'total': total,
            'rated_count': len(rated_records),
            'average_rating': round(avg_rating, 2),
            'by_scenario': scenario_counts,
            'by_style': style_counts,
            'rating_distribution': rating_distribution
        }
