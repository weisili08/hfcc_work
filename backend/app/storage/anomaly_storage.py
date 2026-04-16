"""
异常告警存储模块
提供异常交易告警的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class AnomalyAlertStorage(BaseStorage):
    """
    异常告警存储类
    
    存储字段：
    - id: 唯一标识
    - customer_id: 客户ID
    - customer_name: 客户姓名
    - alert_type: 告警类型 (large_redemption/频繁投诉/unusual_transaction/dormant_account)
    - severity: 严重程度 (critical/high/medium/low)
    - description: 告警描述
    - analysis: AI分析结果
    - status: 状态 (new/investigating/resolved/dismissed)
    - created_at: 创建时间
    - resolved_at: 解决时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化异常告警存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'anomaly_alerts.json')
    
    def list_by_severity(self, severity: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按严重程度筛选告警
        
        Args:
            severity: 严重程度 (critical/high/medium/low)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'severity': severity},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def list_by_status(self, status: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按状态筛选告警
        
        Args:
            status: 状态 (new/investigating/resolved/dismissed)
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
    
    def list_by_customer(self, customer_id: str) -> list:
        """
        获取指定客户的所有告警
        
        Args:
            customer_id: 客户ID
        
        Returns:
            list: 告警列表
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            if item.get('customer_id') == customer_id:
                results.append(item.copy())
        
        # 按时间倒序
        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return results
    
    def update_status(self, alert_id: str, status: str, analysis: str = None) -> dict:
        """
        更新告警状态
        
        Args:
            alert_id: 告警ID
            status: 新状态 (new/investigating/resolved/dismissed)
            analysis: AI分析结果（可选）
        
        Returns:
            dict: 更新后的记录
        """
        updates = {'status': status}
        
        if analysis:
            updates['analysis'] = analysis
        
        # 如果状态变为resolved或dismissed，记录解决时间
        if status in ['resolved', 'dismissed']:
            updates['resolved_at'] = self._get_timestamp()
        
        return self.update(alert_id, updates)
    
    def get_statistics(self) -> dict:
        """
        获取告警统计信息
        
        Returns:
            dict: 统计信息
        """
        data = self._load()
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        status_counts = {'new': 0, 'investigating': 0, 'resolved': 0, 'dismissed': 0}
        type_counts = {}
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            # 统计严重程度
            severity = item.get('severity')
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            # 统计状态
            status = item.get('status')
            if status in status_counts:
                status_counts[status] += 1
            
            # 统计类型
            alert_type = item.get('alert_type')
            if alert_type:
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        total = sum(severity_counts.values())
        unresolved = status_counts['new'] + status_counts['investigating']
        
        return {
            'total': total,
            'unresolved': unresolved,
            'severity_distribution': severity_counts,
            'status_distribution': status_counts,
            'type_distribution': type_counts
        }
    
    def create_alert(self, customer_id: str, customer_name: str, alert_type: str,
                     severity: str, description: str) -> dict:
        """
        创建告警记录
        
        Args:
            customer_id: 客户ID
            customer_name: 客户姓名
            alert_type: 告警类型
            severity: 严重程度
            description: 告警描述
        
        Returns:
            dict: 创建的告警记录
        """
        alert = {
            'customer_id': customer_id,
            'customer_name': customer_name,
            'alert_type': alert_type,
            'severity': severity,
            'description': description,
            'analysis': None,
            'status': 'new'
        }
        
        return self.create(alert)
