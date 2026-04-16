"""
合规检查存储模块
提供合规检查记录的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class ComplianceCheckStorage(BaseStorage):
    """
    合规检查记录存储类
    
    存储字段：
    - id: 检查ID (comp_{uuid})
    - check_type: 检查类型 (content/process/transaction/communication)
    - target_description: 检查目标描述
    - content_to_check: 待检查内容
    - result: 检查结果 (pass/warning/violation)
    - risk_level: 风险等级 (low/medium/high/critical)
    - findings: 发现问题列表
    - suggestions: 改进建议列表
    - checked_by: 检查人
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化合规检查存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'compliance_checks.json')
    
    def create_check(self, check_data: dict) -> dict:
        """
        创建合规检查记录
        
        Args:
            check_data: 检查数据字典
            
        Returns:
            dict: 创建后的完整记录
        """
        # 设置默认值
        if 'result' not in check_data:
            check_data['result'] = 'pass'
        if 'risk_level' not in check_data:
            check_data['risk_level'] = 'low'
        if 'findings' not in check_data:
            check_data['findings'] = []
        if 'suggestions' not in check_data:
            check_data['suggestions'] = []
        
        return self.create(check_data)
    
    def get_check_by_id(self, check_id: str) -> dict:
        """
        按ID获取检查记录
        
        Args:
            check_id: 检查ID
            
        Returns:
            dict: 检查记录，不存在返回None
        """
        return self.get(check_id)
    
    def update_check(self, check_id: str, updates: dict) -> dict:
        """
        更新检查记录
        
        Args:
            check_id: 检查ID
            updates: 更新的字段
            
        Returns:
            dict: 更新后的记录
        """
        return self.update(check_id, updates)
    
    def list_checks(self, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        """
        列表查询检查记录
        
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
    
    def get_checks_by_type(self, check_type: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按检查类型获取记录
        
        Args:
            check_type: 检查类型
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'check_type': check_type},
            page=page,
            page_size=page_size
        )
    
    def get_checks_by_result(self, result: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按检查结果获取记录
        
        Args:
            result: 检查结果
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'result': result},
            page=page,
            page_size=page_size
        )
    
    def get_checks_by_risk_level(self, risk_level: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按风险等级获取记录
        
        Args:
            risk_level: 风险等级
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'risk_level': risk_level},
            page=page,
            page_size=page_size
        )
    
    def get_statistics(self) -> dict:
        """
        获取合规检查统计
        
        Returns:
            dict: 统计数据
        """
        data = self._load()
        
        # 过滤已删除记录
        data = [item for item in data if item.get('deleted_at') is None]
        
        total = len(data)
        
        # 按结果统计
        by_result = {'pass': 0, 'warning': 0, 'violation': 0}
        for item in data:
            result = item.get('result', 'pass')
            if result in by_result:
                by_result[result] += 1
        
        # 按风险等级统计
        by_risk = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for item in data:
            risk = item.get('risk_level', 'low')
            if risk in by_risk:
                by_risk[risk] += 1
        
        # 按检查类型统计
        by_type = {}
        for item in data:
            check_type = item.get('check_type', 'unknown')
            by_type[check_type] = by_type.get(check_type, 0) + 1
        
        return {
            'total': total,
            'by_result': by_result,
            'by_risk_level': by_risk,
            'by_type': by_type,
            'pass_rate': round(by_result['pass'] / total * 100, 2) if total > 0 else 0
        }
