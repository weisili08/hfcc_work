"""
认证授权API路由模块
提供用户登录、登出、个人信息等接口
"""

import logging
from flask import Blueprint, request, current_app

from app.utils.response import (
    success_response, bad_request, unauthorized, 
    internal_error
)
from app.utils.auth import (
    generate_token, login_required, get_current_user
)
from app.storage.user_storage import UserStorage


logger = logging.getLogger(__name__)

# 创建蓝图
auth_bp = Blueprint('auth', __name__)


def get_user_storage():
    """获取用户存储实例"""
    data_dir = current_app.config.get('DATA_DIR', './data')
    return UserStorage(data_dir)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体:
        {
            "username": "用户名",
            "password": "密码"
        }
    
    响应:
        {
            "data": {
                "token": "JWT Token",
                "user": {用户基本信息}
            }
        }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return bad_request(
                error_code="INVALID_REQUEST",
                message="请求体不能为空"
            )
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 参数校验
        if not username:
            return bad_request(
                error_code="MISSING_USERNAME",
                message="用户名不能为空"
            )
        
        if not password:
            return bad_request(
                error_code="MISSING_PASSWORD",
                message="密码不能为空"
            )
        
        # 验证用户凭据
        user_storage = get_user_storage()
        user = user_storage.authenticate(username, password)
        
        if not user:
            logger.warning(f"Login failed for username: {username}")
            return unauthorized(
                error_code="INVALID_CREDENTIALS",
                message="用户名或密码错误"
            )
        
        # 生成JWT Token
        token = generate_token(
            user_id=user['id'],
            role=user['role'],
            username=user['username']
        )
        
        logger.info(f"User logged in: {username} (ID: {user['id']})")
        
        return success_response(
            data={
                "token": token,
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "name": user.get('name'),
                    "role": user['role'],
                    "email": user.get('email'),
                    "department": user.get('department')
                }
            },
            message="登录成功"
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return internal_error(
            error_code="LOGIN_ERROR",
            message="登录过程中发生错误"
        )


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    用户登出
    
    客户端需要清除本地存储的Token
    服务端记录登出日志
    
    响应:
        {
            "data": {"message": "登出成功"}
        }
    """
    try:
        current_user = get_current_user()
        user_id = current_user.get('user_id') if current_user else 'unknown'
        
        logger.info(f"User logged out: {user_id}")
        
        # 注意：JWT是无状态的，服务端无法真正"销毁"token
        # 客户端需要自行清除token
        # 生产环境可以使用黑名单机制
        
        return success_response(
            data={"message": "登出成功"},
            message="登出成功"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return internal_error(
            error_code="LOGOUT_ERROR",
            message="登出过程中发生错误"
        )


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    获取当前用户信息
    
    需要登录（携带有效JWT Token）
    
    响应:
        {
            "data": {用户详细信息}
        }
    """
    try:
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # 获取完整用户信息
        user_storage = get_user_storage()
        user = user_storage.get_safe(user_id)
        
        if not user:
            return unauthorized(
                error_code="USER_NOT_FOUND",
                message="用户不存在或已被删除"
            )
        
        return success_response(
            data=user,
            message="获取用户信息成功"
        )
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return internal_error(
            error_code="PROFILE_ERROR",
            message="获取用户信息失败"
        )


@auth_bp.route('/refresh', methods=['POST'])
@login_required
def refresh_token():
    """
    刷新JWT Token
    
    使用当前有效的Token换取新的Token，延长有效期
    
    响应:
        {
            "data": {
                "token": "新的JWT Token"
            }
        }
    """
    try:
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        role = current_user.get('role')
        
        # 获取用户信息以刷新username等额外信息
        user_storage = get_user_storage()
        user = user_storage.get_safe(user_id)
        
        if not user:
            return unauthorized(
                error_code="USER_NOT_FOUND",
                message="用户不存在"
            )
        
        # 生成新Token
        new_token = generate_token(
            user_id=user_id,
            role=role,
            username=user.get('username')
        )
        
        logger.info(f"Token refreshed for user: {user_id}")
        
        return success_response(
            data={"token": new_token},
            message="Token刷新成功"
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return internal_error(
            error_code="REFRESH_ERROR",
            message="刷新Token失败"
        )
