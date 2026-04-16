"""
统一响应格式模块
提供标准化的API响应格式
"""

from datetime import datetime, timezone
from flask import jsonify, request


def get_current_timestamp():
    """获取当前UTC时间戳（ISO 8601格式）"""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def get_trace_id():
    """获取当前请求的trace_id"""
    return getattr(request, 'trace_id', None) or 'unknown'


def success_response(data=None, message="success", code=200):
    """
    统一成功响应格式
    
    符合API接口规格文档中的成功响应格式：
    {
        "trace_id": "tr_abc123...",
        "data": { ... },
        "meta": {
            "timestamp": "2026-04-15T10:30:00Z",
            "api_version": "v1"
        }
    }
    
    Args:
        data: 响应数据（任意类型）
        message: 成功消息
        code: HTTP状态码
    
    Returns:
        tuple: (jsonify响应, HTTP状态码)
    """
    response = {
        "trace_id": get_trace_id(),
        "data": data,
        "meta": {
            "timestamp": get_current_timestamp(),
            "api_version": "v1",
            "message": message
        }
    }
    return jsonify(response), code


def error_response(code, error_code, message, details=None):
    """
    统一错误响应格式
    
    符合API接口规格文档中的错误响应格式：
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "错误描述",
            "details": { ... },
            "trace_id": "tr_abc123..."
        },
        "meta": {
            "timestamp": "2026-04-15T10:30:00Z",
            "api_version": "v1"
        }
    }
    
    Args:
        code: HTTP状态码
        error_code: 错误代码（如 INVALID_REQUEST）
        message: 错误描述
        details: 额外详情（字典类型）
    
    Returns:
        tuple: (jsonify响应, HTTP状态码)
    """
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "trace_id": get_trace_id()
        },
        "meta": {
            "timestamp": get_current_timestamp(),
            "api_version": "v1"
        }
    }
    return jsonify(response), code


def paginated_response(items, total, page, page_size, extra_data=None):
    """
    分页响应格式
    
    符合API接口规格文档中的分页响应格式：
    {
        "trace_id": "tr_abc123...",
        "data": {
            "items": [...],
            "pagination": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        },
        "meta": { ... }
    }
    
    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页条数
        extra_data: 额外的响应数据（可选）
    
    Returns:
        tuple: (jsonify响应, HTTP状态码200)
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }
    
    # 合并额外数据
    if extra_data and isinstance(extra_data, dict):
        data.update(extra_data)
    
    return success_response(data=data)


# 预定义的错误响应快捷函数

def bad_request(error_code="INVALID_REQUEST", message="请求参数错误", details=None):
    """400 Bad Request"""
    return error_response(400, error_code, message, details)


def unauthorized(error_code="UNAUTHORIZED", message="未授权访问", details=None):
    """401 Unauthorized"""
    return error_response(401, error_code, message, details)


def forbidden(error_code="FORBIDDEN", message="禁止访问", details=None):
    """403 Forbidden"""
    return error_response(403, error_code, message, details)


def not_found(error_code="NOT_FOUND", message="资源不存在", details=None):
    """404 Not Found"""
    return error_response(404, error_code, message, details)


def conflict(error_code="CONFLICT", message="资源冲突", details=None):
    """409 Conflict"""
    return error_response(409, error_code, message, details)


def validation_error(error_code="VALIDATION_ERROR", message="数据校验失败", details=None):
    """422 Validation Error"""
    return error_response(422, error_code, message, details)


def rate_limited(error_code="RATE_LIMITED", message="请求频率超限", details=None):
    """429 Rate Limited"""
    if details is None:
        details = {"retry_after": 60}
    return error_response(429, error_code, message, details)


def internal_error(error_code="INTERNAL_ERROR", message="服务器内部错误", details=None):
    """500 Internal Server Error"""
    return error_response(500, error_code, message, details)


def service_unavailable(error_code="SERVICE_UNAVAILABLE", message="服务暂时不可用", details=None):
    """503 Service Unavailable"""
    return error_response(503, error_code, message, details)


def llm_unavailable(error_code="LLM_UNAVAILABLE", message="所有LLM服务不可用", details=None):
    """503 LLM Unavailable"""
    if details is None:
        details = {"fallback": "local_kb"}
    return error_response(503, error_code, message, details)
