"""
客户画像存储模块
提供客户画像数据的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class CustomerProfileStorage(BaseStorage):
    """
    客户画像存储类
    
    存储字段：
    - id: 唯一标识
    - customer_name: 客户姓名
    - age_range: 年龄段
    - gender: 性别
    - risk_level: 风险等级
    - aum_range: 资产规模区间
    - product_preferences: 产品偏好列表
    - behavior_tags: 行为标签列表
    - activity_score: 活跃度评分(0-100)
    - loyalty_score: 忠诚度评分(0-100)
    - value_tier: 价值分层(high/medium/low)
    - last_contact: 最后联系时间
    - analysis_summary: AI分析摘要
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化客户画像存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'customer_profiles.json')
    
    def find_by_tags(self, tags: list) -> list:
        """
        按标签搜索客户画像
        
        Args:
            tags: 标签列表
        
        Returns:
            list: 匹配的客户画像列表
        """
        if not tags:
            return []
        
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            item_tags = item.get('behavior_tags', [])
            # 只要有一个标签匹配即可
            if any(tag in item_tags for tag in tags):
                results.append(item.copy())
        
        return results
    
    def find_by_value_tier(self, tier: str) -> list:
        """
        按价值分层筛选客户
        
        Args:
            tier: 价值分层 (high/medium/low)
        
        Returns:
            list: 匹配的客户画像列表
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            if item.get('value_tier') == tier:
                results.append(item.copy())
        
        return results
    
    def find_similar_profiles(self, profile_id: str, top_n: int = 5) -> list:
        """
        查找相似客户画像
        
        基于标签、风险等级、资产规模等维度计算相似度
        
        Args:
            profile_id: 参考客户画像ID
            top_n: 返回数量
        
        Returns:
            list: 相似客户画像列表（包含相似度分数）
        """
        target = self.get(profile_id)
        if not target:
            return []
        
        data = self._load()
        similarities = []
        
        target_tags = set(target.get('behavior_tags', []))
        target_risk = target.get('risk_level', '')
        target_aum = target.get('aum_range', '')
        target_prefs = set(target.get('product_preferences', []))
        
        for item in data:
            if item.get('id') == profile_id or item.get('deleted_at') is not None:
                continue
            
            # 计算相似度分数
            score = 0
            
            # 标签匹配度（最高40分）
            item_tags = set(item.get('behavior_tags', []))
            if target_tags and item_tags:
                tag_overlap = len(target_tags & item_tags)
                tag_score = min(40, tag_overlap * 10)
                score += tag_score
            
            # 风险等级匹配（20分）
            if item.get('risk_level') == target_risk:
                score += 20
            
            # 资产规模匹配（20分）
            if item.get('aum_range') == target_aum:
                score += 20
            
            # 产品偏好匹配（最高20分）
            item_prefs = set(item.get('product_preferences', []))
            if target_prefs and item_prefs:
                pref_overlap = len(target_prefs & item_prefs)
                pref_score = min(20, pref_overlap * 5)
                score += pref_score
            
            if score > 0:
                item_copy = item.copy()
                item_copy['similarity_score'] = score
                similarities.append(item_copy)
        
        # 按相似度排序并返回前N个
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:top_n]
    
    def get_tag_statistics(self) -> dict:
        """
        获取标签统计信息
        
        Returns:
            dict: 标签统计
        """
        data = self._load()
        tag_counts = {}
        tier_counts = {'high': 0, 'medium': 0, 'low': 0}
        risk_counts = {}
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            # 统计标签
            for tag in item.get('behavior_tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # 统计价值分层
            tier = item.get('value_tier')
            if tier in tier_counts:
                tier_counts[tier] += 1
            
            # 统计风险等级
            risk = item.get('risk_level')
            if risk:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        return {
            'total_profiles': len([i for i in data if i.get('deleted_at') is None]),
            'tag_distribution': tag_counts,
            'tier_distribution': tier_counts,
            'risk_distribution': risk_counts
        }
    
    def update_analysis_summary(self, profile_id: str, summary: str) -> dict:
        """
        更新客户画像的AI分析摘要
        
        Args:
            profile_id: 客户画像ID
            summary: 分析摘要
        
        Returns:
            dict: 更新后的记录
        """
        return self.update(profile_id, {'analysis_summary': summary})
