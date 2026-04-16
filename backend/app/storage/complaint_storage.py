"""
投诉管理存储模块
提供投诉记录的CRUD操作和统计分析
"""

from app.storage.base_storage import BaseStorage


class ComplaintStorage(BaseStorage):
    """
    投诉存储类
    
    字段：
    - id: 唯一标识
    - title: 投诉标题
    - customer_name: 客户姓名
    - customer_phone: 客户电话
    - type: 投诉类型 (product/service/system/other)
    - description: 投诉描述
    - status: 状态 (pending/processing/escalated/resolved/closed)
    - priority: 优先级 (high/medium/low)
    - assignee: 处理人
    - resolution: 解决方案
    - created_by: 创建人
    - created_at: 创建时间
    - updated_at: 更新时间
    - resolved_at: 解决时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化投诉存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'complaints.json')
    
    def get_by_status(self, status: str) -> list:
        """
        按状态查询投诉
        
        Args:
            status: 投诉状态
        
        Returns:
            list: 符合条件的投诉列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('status') == status and item.get('deleted_at') is None
        ]
    
    def get_statistics(self) -> dict:
        """
        获取投诉统计数据
        
        返回：
        - 按状态分布
        - 按类型分布
        - 按优先级分布
        - 总数统计
        
        Returns:
            dict: 统计数据
        """
        data = self._load()
        
        # 过滤已删除记录
        records = [item for item in data if item.get('deleted_at') is None]
        
        # 按状态统计
        status_counts = {}
        for item in records:
            status = item.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 按类型统计
        type_counts = {}
        for item in records:
            complaint_type = item.get('type', 'unknown')
            type_counts[complaint_type] = type_counts.get(complaint_type, 0) + 1
        
        # 按优先级统计
        priority_counts = {}
        for item in records:
            priority = item.get('priority', 'unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # 计算各状态占比
        total = len(records)
        status_distribution = {
            status: {
                'count': count,
                'percentage': round(count / total * 100, 2) if total > 0 else 0
            }
            for status, count in status_counts.items()
        }
        
        # 计算各类型占比
        type_distribution = {
            complaint_type: {
                'count': count,
                'percentage': round(count / total * 100, 2) if total > 0 else 0
            }
            for complaint_type, count in type_counts.items()
        }
        
        return {
            'total': total,
            'by_status': status_distribution,
            'by_type': type_distribution,
            'by_priority': priority_counts,
            'pending_count': status_counts.get('pending', 0),
            'processing_count': status_counts.get('processing', 0),
            'escalated_count': status_counts.get('escalated', 0),
            'resolved_count': status_counts.get('resolved', 0),
            'closed_count': status_counts.get('closed', 0)
        }
    
    def update_status(self, complaint_id: str, status: str, **kwargs) -> dict:
        """
        更新投诉状态
        
        Args:
            complaint_id: 投诉ID
            status: 新状态
            **kwargs: 其他要更新的字段
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {'status': status}
        
        # 如果状态变为resolved，记录解决时间
        if status == 'resolved':
            updates['resolved_at'] = self._get_timestamp()
        
        # 合并其他更新字段
        updates.update(kwargs)
        
        return self.update(complaint_id, updates)
    
    def assign(self, complaint_id: str, assignee: str) -> dict:
        """
        分配投诉给处理人
        
        Args:
            complaint_id: 投诉ID
            assignee: 处理人
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update_status(complaint_id, 'processing', assignee=assignee)
    
    def escalate(self, complaint_id: str) -> dict:
        """
        升级投诉
        
        Args:
            complaint_id: 投诉ID
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update_status(complaint_id, 'escalated')
    
    def resolve(self, complaint_id: str, resolution: str) -> dict:
        """
        解决投诉
        
        Args:
            complaint_id: 投诉ID
            resolution: 解决方案
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update_status(complaint_id, 'resolved', resolution=resolution)
    
    def close(self, complaint_id: str) -> dict:
        """
        关闭投诉
        
        Args:
            complaint_id: 投诉ID
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update_status(complaint_id, 'closed')
