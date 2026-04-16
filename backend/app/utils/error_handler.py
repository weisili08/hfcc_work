"""
全局错误处理模块
注册Flask应用的错误处理器
"""

from flask import Flask
from app.utils.response import (
    bad_request,
    unauthorized,
    forbidden,
    not_found,
    internal_error,
    service_unavailable
)


def register_error_handlers(app: Flask):
    """
    为Flask应用注册全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """处理400错误 - 请求参数错误"""
        description = str(e.description) if hasattr(e, 'description') else "请求参数错误"
        return bad_request(
            error_code="INVALID_REQUEST",
            message=description,
            details={"error_type": "bad_request"}
        )
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        """处理401错误 - 未授权"""
        description = str(e.description) if hasattr(e, 'description') else "未提供有效的认证信息"
        return unauthorized(
            error_code="UNAUTHORIZED",
            message=description,
            details={"error_type": "unauthorized"}
        )
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        """处理403错误 - 禁止访问"""
        description = str(e.description) if hasattr(e, 'description') else "无权访问该资源"
        return forbidden(
            error_code="FORBIDDEN",
            message=description,
            details={"error_type": "forbidden"}
        )
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """处理404错误 - 资源不存在"""
        description = str(e.description) if hasattr(e, 'description') else "请求的资源不存在"
        return not_found(
            error_code="NOT_FOUND",
            message=description,
            details={
                "error_type": "not_found",
                "path": str(e.request.path) if hasattr(e, 'request') else None
            }
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """处理405错误 - 方法不允许"""
        return bad_request(
            error_code="METHOD_NOT_ALLOWED",
            message="HTTP方法不允许",
            details={"error_type": "method_not_allowed"}
        )
    
    @app.errorhandler(408)
    def handle_request_timeout(e):
        """处理408错误 - 请求超时"""
        return service_unavailable(
            error_code="REQUEST_TIMEOUT",
            message="请求处理超时",
            details={"error_type": "request_timeout"}
        )
    
    @app.errorhandler(429)
    def handle_rate_limit(e):
        """处理429错误 - 请求频率超限"""
        retry_after = getattr(e, 'retry_after', 60)
        from app.utils.response import rate_limited
        return rate_limited(
            error_code="RATE_LIMITED",
            message="请求频率超限，请稍后重试",
            details={"retry_after": retry_after}
        )
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """处理500错误 - 服务器内部错误"""
        # 记录错误日志
        app.logger.error(f"Internal Server Error: {str(e)}", exc_info=True)
        return internal_error(
            error_code="INTERNAL_ERROR",
            message="服务器内部错误，请稍后重试",
            details={"error_type": "internal_error"}
        )
    
    @app.errorhandler(502)
    def handle_bad_gateway(e):
        """处理502错误 - 网关错误"""
        return service_unavailable(
            error_code="BAD_GATEWAY",
            message="网关错误",
            details={"error_type": "bad_gateway"}
        )
    
    @app.errorhandler(503)
    def handle_service_unavailable(e):
        """处理503错误 - 服务不可用"""
        description = str(e.description) if hasattr(e, 'description') else "服务暂时不可用"
        return service_unavailable(
            error_code="SERVICE_UNAVAILABLE",
            message=description,
            details={"error_type": "service_unavailable"}
        )
    
    @app.errorhandler(504)
    def handle_gateway_timeout(e):
        """处理504错误 - 网关超时"""
        return service_unavailable(
            error_code="GATEWAY_TIMEOUT",
            message="网关超时",
            details={"error_type": "gateway_timeout"}
        )
    
    # 处理未捕获的异常
    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有未捕获的异常"""
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return internal_error(
            error_code="INTERNAL_ERROR",
            message="服务器发生未知错误",
            details={"error_type": "unhandled_exception", "error_class": type(e).__name__}
        )
    
    # 处理Werkzeug的HTTPException
    try:
        from werkzeug.exceptions import HTTPException
        
        @app.errorhandler(HTTPException)
        def handle_http_exception(e):
            """处理所有HTTP异常"""
            if e.code >= 500:
                app.logger.error(f"HTTP Exception {e.code}: {str(e)}", exc_info=True)
                return internal_error(
                    error_code="INTERNAL_ERROR",
                    message="服务器错误",
                    details={"http_code": e.code}
                )
            elif e.code == 404:
                return not_found(
                    error_code="NOT_FOUND",
                    message=str(e.description),
                    details={"http_code": e.code}
                )
            elif e.code == 405:
                return bad_request(
                    error_code="METHOD_NOT_ALLOWED",
                    message="请求方法不允许",
                    details={"http_code": e.code}
                )
            else:
                return bad_request(
                    error_code="INVALID_REQUEST",
                    message=str(e.description),
                    details={"http_code": e.code}
                )
    except ImportError:
        pass
