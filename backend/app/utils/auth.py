"""
认证工具模块
提供JWT Token生成、验证和权限装饰器
"""

import jwt
import functools
from datetime import datetime, timedelta, timezone
from flask import request, current_app, g

from app.utils.response import unauthorized, forbidden


# JWT配置
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def generate_token(user_id: str, role: str, **extra_claims) -> str:
    """
    生成JWT Token
    
    Args:
        user_id: 用户ID
        role: 用户角色代码
        **extra_claims: 额外的声明数据
        
    Returns:
        str: JWT Token字符串
    """
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    
    # 构建payload
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'type': 'access'
    }
    
    # 添加额外声明
    payload.update(extra_claims)
    
    # 生成token
    token = jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """
    验证JWT Token
    
    Args:
        token: JWT Token字符串
        
    Returns:
        dict | None: 验证成功返回payload，失败返回None
    """
    if not token:
        return None
    
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token已过期
        return None
    except jwt.InvalidTokenError:
        # Token无效
        return None


def get_token_from_request() -> str:
    """
    从请求中提取Token
    
    支持Header: Authorization: Bearer <token>
    
    Returns:
        str | None: Token字符串，未找到返回None
    """
    auth_header = request.headers.get('Authorization', '')
    
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # 移除 "Bearer " 前缀
    
    return None


def get_current_user() -> dict:
    """
    获取当前登录用户信息
    
    需要在login_required装饰器之后使用
    
    Returns:
        dict | None: 当前用户信息
    """
    return getattr(g, 'current_user', None)


def login_required(f):
    """
    登录校验装饰器
    
    验证请求中的JWT Token，将用户信息存入g.current_user
    
    使用方式:
        @app.route('/protected')
        @login_required
        def protected_route():
            user = get_current_user()
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return unauthorized(
                error_code="MISSING_TOKEN",
                message="缺少访问令牌，请在Authorization Header中提供Bearer Token"
            )
        
        payload = verify_token(token)
        
        if not payload:
            return unauthorized(
                error_code="INVALID_TOKEN",
                message="访问令牌无效或已过期，请重新登录"
            )
        
        # 将用户信息存入g对象
        g.current_user = {
            'user_id': payload.get('user_id'),
            'role': payload.get('role'),
            'exp': payload.get('exp')
        }
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*allowed_roles):
    """
    角色权限校验装饰器
    
    验证当前用户是否具有指定角色之一
    
    使用方式:
        @app.route('/admin-only')
        @login_required
        @require_role('admin', 'supervisor')
        def admin_route():
            ...
    
    Args:
        *allowed_roles: 允许的角色代码列表
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            
            if not current_user:
                return unauthorized(
                    error_code="NOT_AUTHENTICATED",
                    message="请先登录"
                )
            
            user_role = current_user.get('role')
            
            # 管理员拥有所有权限
            if user_role == 'admin':
                return f(*args, **kwargs)
            
            # 检查角色是否在允许列表中
            if user_role not in allowed_roles:
                return forbidden(
                    error_code="INSUFFICIENT_PERMISSIONS",
                    message=f"当前角色 '{user_role}' 无权访问此资源",
                    details={"required_roles": list(allowed_roles)}
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permission(permission: str):
    """
    权限校验装饰器（基于角色的权限检查）
    
    需要配合RoleStorage使用，检查用户角色是否拥有指定权限
    
    使用方式:
        @app.route('/kb/manage')
        @login_required
        @require_permission('kb:manage')
        def manage_kb():
            ...
    
    Args:
        permission: 权限标识，如 'kb:read', 'kb:write'
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            from app.storage.role_storage import RoleStorage
            
            current_user = get_current_user()
            
            if not current_user:
                return unauthorized(
                    error_code="NOT_AUTHENTICATED",
                    message="请先登录"
                )
            
            user_role = current_user.get('role')
            data_dir = current_app.config.get('DATA_DIR', './data')
            role_storage = RoleStorage(data_dir)
            
            # 检查权限
            permissions = role_storage.get_permissions(user_role)
            
            # 管理员拥有所有权限
            if '*:*' in permissions or permission in permissions:
                return f(*args, **kwargs)
            
            return forbidden(
                error_code="PERMISSION_DENIED",
                message=f"缺少权限: {permission}",
                details={"required_permission": permission}
            )
        
        return decorated_function
    return decorator
