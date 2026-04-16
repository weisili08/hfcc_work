"""
报表存储模块
提供报表数据的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class ReportStorage(BaseStorage):
    """
    报表存储类
    
    存储字段：
    - id: 唯一标识
    - title: 报表标题
    - type: 报表类型 (daily/weekly/monthly/custom)
    - category: 报表类别 (service/complaint/quality/customer)
    - parameters: 报表参数
    - content: 报表内容
    - summary: AI生成的摘要
    - status: 状态 (draft/generating/completed/failed)
    - created_by: 创建者
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化报表存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'reports.json')
    
    def list_by_type(self, report_type: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按类型筛选报表
        
        Args:
            report_type: 报表类型 (daily/weekly/monthly/custom)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'type': report_type},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def list_by_category(self, category: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按类别筛选报表
        
        Args:
            category: 报表类别 (service/complaint/quality/customer)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'category': category},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def list_by_status(self, status: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按状态筛选报表
        
        Args:
            status: 状态 (draft/generating/completed/failed)
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
    
    def update_status(self, report_id: str, status: str) -> dict:
        """
        更新报表状态
        
        Args:
            report_id: 报表ID
            status: 新状态 (draft/generating/completed/failed)
        
        Returns:
            dict: 更新后的记录
        """
        return self.update(report_id, {'status': status})
    
    def update_content(self, report_id: str, content: dict, summary: str = None) -> dict:
        """
        更新报表内容和摘要
        
        Args:
            report_id: 报表ID
            content: 报表内容
            summary: AI摘要（可选）
        
        Returns:
            dict: 更新后的记录
        """
        updates = {'content': content}
        if summary:
            updates['summary'] = summary
        
        return self.update(report_id, updates)
    
    def get_statistics(self) -> dict:
        """
        获取报表统计信息
        
        Returns:
            dict: 统计信息
        """
        data = self._load()
        
        type_counts = {'daily': 0, 'weekly': 0, 'monthly': 0, 'custom': 0}
        category_counts = {'service': 0, 'complaint': 0, 'quality': 0, 'customer': 0}
        status_counts = {'draft': 0, 'generating': 0, 'completed': 0, 'failed': 0}
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            # 统计类型
            report_type = item.get('type')
            if report_type in type_counts:
                type_counts[report_type] += 1
            
            # 统计类别
            category = item.get('category')
            if category in category_counts:
                category_counts[category] += 1
            
            # 统计状态
            status = item.get('status')
            if status in status_counts:
                status_counts[status] += 1
        
        total = sum(type_counts.values())
        completed = status_counts['completed']
        
        return {
            'total': total,
            'completed': completed,
            'type_distribution': type_counts,
            'category_distribution': category_counts,
            'status_distribution': status_counts
        }
    
    def create_report(self, title: str, report_type: str, category: str,
                     parameters: dict, created_by: str = 'system') -> dict:
        """
        创建报表记录
        
        Args:
            title: 报表标题
            report_type: 报表类型
            category: 报表类别
            parameters: 报表参数
            created_by: 创建者
        
        Returns:
            dict: 创建的报表记录
        """
        report = {
            'title': title,
            'type': report_type,
            'category': category,
            'parameters': parameters,
            'content': None,
            'summary': None,
            'status': 'draft',
            'created_by': created_by
        }
        
        return self.create(report)
