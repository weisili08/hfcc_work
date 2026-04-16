"""
用户存储模块
提供用户数据的CRUD操作和认证功能
"""

import hashlib
from app.storage.base_storage import BaseStorage


class UserStorage(BaseStorage):
    """
    用户存储类
    
    字段：
    - id: 唯一标识
    - username: 用户名（唯一）
    - password_hash: 密码SHA256哈希值
    - name: 显示名称
    - role: 角色代码
    - email: 邮箱
    - phone: 电话
    - department: 部门
    - status: 状态 (active/inactive)
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化用户存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'users.json')
    
    def _get_id_prefix(self) -> str:
        """获取用户ID前缀"""
        return 'user'
    
    def _hash_password(self, password: str) -> str:
        """
        使用SHA256哈希密码
        
        注意：这是教学级别的简单实现，生产环境应使用bcrypt等更安全的方案
        
        Args:
            password: 明文密码
            
        Returns:
            str: SHA256哈希值
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def create(self, item: dict) -> dict:
        """
        创建用户
        
        如果提供了password字段，会自动转换为password_hash
        
        Args:
            item: 用户数据
            
        Returns:
            dict: 创建后的用户记录（不含密码哈希）
        """
        # 复制数据避免修改原始对象
        record = item.copy()
        
        # 处理密码：如果有password字段，转换为password_hash
        if 'password' in record:
            password = record.pop('password')
            record['password_hash'] = self._hash_password(password)
        
        # 检查用户名是否已存在
        if self.get_by_username(record.get('username')):
            raise ValueError(f"用户名 '{record['username']}' 已存在")
        
        # 调用父类create方法
        created = super().create(record)
        
        # 返回时移除password_hash字段
        result = created.copy()
        result.pop('password_hash', None)
        return result
    
    def get_by_username(self, username: str) -> dict:
        """
        按用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            dict | None: 用户记录，不存在返回None
        """
        data = self._load()
        for item in data:
            if item.get('username') == username and item.get('deleted_at') is None:
                return item.copy()
        return None
    
    def get_safe(self, user_id: str) -> dict:
        """
        获取用户信息（安全版本，不含密码哈希）
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict | None: 用户记录（不含password_hash）
        """
        user = self.get(user_id)
        if user:
            user = user.copy()
            user.pop('password_hash', None)
        return user
    
    def authenticate(self, username: str, password: str) -> dict:
        """
        验证用户登录凭据
        
        Args:
            username: 用户名
            password: 明文密码
            
        Returns:
            dict | None: 验证成功返回用户记录（不含密码），失败返回None
        """
        # 获取用户（包含密码哈希）
        data = self._load()
        user = None
        for item in data:
            if item.get('username') == username and item.get('deleted_at') is None:
                user = item
                break
        
        if not user:
            return None
        
        # 检查用户状态
        if user.get('status') != 'active':
            return None
        
        # 验证密码
        password_hash = self._hash_password(password)
        if user.get('password_hash') != password_hash:
            return None
        
        # 返回用户信息（不含密码哈希）
        result = user.copy()
        result.pop('password_hash', None)
        return result
    
    def update_password(self, user_id: str, new_password: str) -> dict:
        """
        更新用户密码
        
        Args:
            user_id: 用户ID
            new_password: 新密码
            
        Returns:
            dict | None: 更新后的用户记录
        """
        password_hash = self._hash_password(new_password)
        return self.update(user_id, {'password_hash': password_hash})
    
    def list(self, **kwargs) -> dict:
        """
        列出用户（覆盖父类方法，移除密码哈希）
        
        Returns:
            dict: 分页结果，items中不含password_hash
        """
        result = super().list(**kwargs)
        # 移除每个用户的密码哈希
        for item in result['items']:
            item.pop('password_hash', None)
        return result
