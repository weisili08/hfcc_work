"""
流失风险存储模块
提供客户流失风险数据的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class ChurnRiskStorage(BaseStorage):
    """
    流失风险存储类
    
    存储字段：
    - id: 唯一标识
    - customer_id: 客户ID
    - customer_name: 客户姓名
    - risk_score: 风险评分 (0-100)
    - risk_level: 风险等级 (critical/high/medium/low)
    - risk_factors: 风险因素列表
    - retention_suggestions: 挽留建议列表
    - status: 状态 (new/contacted/retained/churned)
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化流失风险存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'churn_risks.json')
    
    def list_by_risk_level(self, risk_level: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按风险等级筛选
        
        Args:
            risk_level: 风险等级 (critical/high/medium/low)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'risk_level': risk_level},
            page=page,
            page_size=page_size,
            sort_by='risk_score',
            sort_order='desc'
        )
    
    def list_by_status(self, status: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按状态筛选
        
        Args:
            status: 状态 (new/contacted/retained/churned)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'status': status},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def get_by_customer(self, customer_id: str) -> dict:
        """
        获取指定客户的流失风险记录
        
        Args:
            customer_id: 客户ID
        
        Returns:
            dict: 风险记录，不存在返回None
        """
        data = self._load()
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            if item.get('customer_id') == customer_id:
                return item.copy()
        
        return None
    
    def update_status(self, risk_id: str, status: str) -> dict:
        """
        更新风险状态
        
        Args:
            risk_id: 风险记录ID
            status: 新状态 (new/contacted/retained/churned)
        
        Returns:
            dict: 更新后的记录
        """
        return self.update(risk_id, {'status': status})
    
    def update_retention_plan(self, risk_id: str, suggestions: list) -> dict:
        """
        更新挽留建议
        
        Args:
            risk_id: 风险记录ID
            suggestions: 挽留建议列表
        
        Returns:
            dict: 更新后的记录
        """
        return self.update(risk_id, {'retention_suggestions': suggestions})
    
    def get_high_risk_customers(self, threshold: int = 70) -> list:
        """
        获取高风险客户列表
        
        Args:
            threshold: 风险分数阈值
        
        Returns:
            list: 高风险客户列表
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            if item.get('risk_score', 0) >= threshold:
                results.append(item.copy())
        
        # 按风险分数倒序
        results.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        return results
    
    def get_statistics(self) -> dict:
        """
        获取流失风险统计信息
        
        Returns:
            dict: 统计信息
        """
        data = self._load()
        
        level_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        status_counts = {'new': 0, 'contacted': 0, 'retained': 0, 'churned': 0}
        
        total_score = 0
        high_risk_count = 0
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            # 统计风险等级
            level = item.get('risk_level')
            if level in level_counts:
                level_counts[level] += 1
            
            # 统计状态
            status = item.get('status')
            if status in status_counts:
                status_counts[status] += 1
            
            # 计算平均分
            score = item.get('risk_score', 0)
            total_score += score
            
            if score >= 70:
                high_risk_count += 1
        
        total = sum(level_counts.values())
        avg_score = total_score / total if total > 0 else 0
        
        return {
            'total': total,
            'high_risk_count': high_risk_count,
            'average_risk_score': round(avg_score, 2),
            'level_distribution': level_counts,
            'status_distribution': status_counts
        }
    
    def create_risk_record(self, customer_id: str, customer_name: str,
                          risk_score: int, risk_level: str,
                          risk_factors: list = None) -> dict:
        """
        创建流失风险记录
        
        Args:
            customer_id: 客户ID
            customer_name: 客户姓名
            risk_score: 风险评分 (0-100)
            risk_level: 风险等级
            risk_factors: 风险因素列表
        
        Returns:
            dict: 创建的记录
        """
        record = {
            'customer_id': customer_id,
            'customer_name': customer_name,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors or [],
            'retention_suggestions': [],
            'status': 'new'
        }
        
        return self.create(record)
