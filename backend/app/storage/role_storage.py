"""
角色存储模块
提供角色数据的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class RoleStorage(BaseStorage):
    """
    角色存储类
    
    字段：
    - id: 唯一标识
    - name: 角色名称
    - code: 角色代码 (admin/supervisor/agent/manager/analyst/compliance)
    - permissions: 权限列表
    - description: 角色描述
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化角色存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'roles.json')
    
    def _get_id_prefix(self) -> str:
        """获取角色ID前缀"""
        return 'role'
    
    def get_by_code(self, code: str) -> dict:
        """
        按角色代码获取角色
        
        Args:
            code: 角色代码
            
        Returns:
            dict | None: 角色记录，不存在返回None
        """
        data = self._load()
        for item in data:
            if item.get('code') == code and item.get('deleted_at') is None:
                return item.copy()
        return None
    
    def create(self, item: dict) -> dict:
        """
        创建角色
        
        Args:
            item: 角色数据
            
        Returns:
            dict: 创建后的角色记录
            
        Raises:
            ValueError: 角色代码已存在
        """
        # 检查角色代码是否已存在
        if self.get_by_code(item.get('code')):
            raise ValueError(f"角色代码 '{item['code']}' 已存在")
        
        return super().create(item)
    
    def get_permissions(self, code: str) -> list:
        """
        获取角色的权限列表
        
        Args:
            code: 角色代码
            
        Returns:
            list: 权限列表，角色不存在返回空列表
        """
        role = self.get_by_code(code)
        if role:
            return role.get('permissions', [])
        return []
    
    def has_permission(self, code: str, permission: str) -> bool:
        """
        检查角色是否有指定权限
        
        Args:
            code: 角色代码
            permission: 权限标识
            
        Returns:
            bool: 是否有该权限
        """
        permissions = self.get_permissions(code)
        return permission in permissions
    
    def initialize_default_roles(self):
        """
        初始化默认角色
        
        如果角色存储为空，则创建预定义的6个角色
        """
        data = self._load()
        if data:  # 已有数据，跳过
            return
        
        default_roles = [
            {
                "name": "系统管理员",
                "code": "admin",
                "permissions": [
                    "user:manage", "role:manage", "system:config",
                    "kb:manage", "kb:read", "kb:write", "kb:delete",
                    "qa:manage", "qa:read", "qa:write",
                    "complaint:manage", "quality:manage",
                    "analytics:read", "report:manage",
                    "*:*"  # 管理员拥有所有权限
                ],
                "description": "系统管理员，拥有所有权限"
            },
            {
                "name": "客服主管",
                "code": "supervisor",
                "permissions": [
                    "kb:manage", "kb:read", "kb:write",
                    "qa:manage", "qa:read", "qa:write",
                    "complaint:manage", "complaint:read", "complaint:write",
                    "quality:manage", "quality:read",
                    "agent:monitor", "agent:evaluate"
                ],
                "description": "客服团队主管，负责团队管理和质量监督"
            },
            {
                "name": "客服代表",
                "code": "agent",
                "permissions": [
                    "kb:read",
                    "qa:read", "qa:write",
                    "complaint:read", "complaint:write",
                    "customer:read", "customer:write"
                ],
                "description": "一线客服人员，处理客户咨询和投诉"
            },
            {
                "name": "客户经理",
                "code": "manager",
                "permissions": [
                    "customer:manage", "customer:read", "customer:write",
                    "portfolio:read", "portfolio:manage",
                    "hnw:manage", "care:manage",
                    "kb:read", "qa:read"
                ],
                "description": "高净值客户经理，负责客户关系维护"
            },
            {
                "name": "数据分析师",
                "code": "analyst",
                "permissions": [
                    "analytics:read", "analytics:write",
                    "report:read", "report:write", "report:manage",
                    "sentiment:read", "churn:read",
                    "kb:read"
                ],
                "description": "数据分析师，负责数据分析和报告生成"
            },
            {
                "name": "合规专员",
                "code": "compliance",
                "permissions": [
                    "compliance:read", "compliance:manage",
                    "complaint:read", "quality:read",
                    "audit:read", "audit:write",
                    "kb:read", "qa:read"
                ],
                "description": "合规专员，负责合规检查和审计"
            }
        ]
        
        for role_data in default_roles:
            try:
                super().create(role_data)
            except ValueError:
                pass  # 已存在，跳过
