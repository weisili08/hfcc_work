"""
系统健康检查和能力探测路由
提供系统状态监控接口
"""

import os
import platform
from datetime import datetime, timezone
from flask import Blueprint, current_app

from app.utils.response import success_response
from app.services.llm_service import LLMService

# 创建蓝图
health_bp = Blueprint('health', __name__)

# 应用启动时间（用于计算运行时间）
_start_time = datetime.now(timezone.utc)


def _get_uptime_seconds() -> int:
    """获取系统运行时间（秒）"""
    return int((datetime.now(timezone.utc) - _start_time).total_seconds())


def _format_uptime(seconds: int) -> str:
    """格式化运行时间为人类可读字符串"""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}天")
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if not parts or secs > 0:
        parts.append(f"{secs}秒")
    
    return "".join(parts)


def _check_storage_health() -> str:
    """检查存储服务健康状态"""
    try:
        data_dir = current_app.config.get('DATA_DIR', './data')
        if os.path.exists(data_dir) and os.access(data_dir, os.W_OK):
            return "healthy"
        else:
            return "unhealthy"
    except Exception:
        return "unhealthy"


def _check_llm_health() -> dict:
    """检查LLM服务健康状态"""
    try:
        llm_service = LLMService(current_app.config)
        health = llm_service.health_check()
        
        result = {}
        # 主LLM状态
        if health['primary_available']:
            result['llm_primary'] = "healthy"
        else:
            result['llm_primary'] = "unavailable"
        
        # 备用LLM状态
        if health['backup_available']:
            result['llm_backup'] = "healthy"
        else:
            result['llm_backup'] = "unavailable"
        
        return result
    except Exception as e:
        current_app.logger.error(f"LLM health check failed: {str(e)}")
        return {
            'llm_primary': 'unknown',
            'llm_backup': 'unknown'
        }


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    返回服务整体状态、版本、运行时间等信息
    
    GET /api/v1/system/health
    
    Returns:
        {
            "trace_id": "tr_xxx",
            "data": {
                "status": "healthy",  # healthy/degraded/unhealthy
                "version": "1.0.0",
                "timestamp": "2026-04-15T10:30:00Z",
                "uptime_seconds": 3600,
                "uptime_formatted": "1小时",
                "environment": "development",
                "python_version": "3.10.0",
                "platform": "Darwin-22.0.0-x86_64",
                "services": {
                    "api": "healthy",
                    "storage": "healthy",
                    "llm_primary": "healthy",
                    "llm_backup": "unavailable"
                }
            },
            "meta": {...}
        }
    """
    # 检查各服务状态
    storage_status = _check_storage_health()
    llm_status = _check_llm_health()
    
    # 确定整体状态
    services = {
        "api": "healthy",
        "storage": storage_status,
        **llm_status
    }
    
    # 判断整体状态
    if storage_status == "unhealthy":
        overall_status = "unhealthy"
    elif llm_status.get('llm_primary') == "unavailable":
        overall_status = "degraded"  # 主LLM不可用但服务仍可运行
    else:
        overall_status = "healthy"
    
    uptime_seconds = _get_uptime_seconds()
    
    data = {
        "status": overall_status,
        "version": current_app.config.get('APP_VERSION', '1.0.0'),
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": _format_uptime(uptime_seconds),
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "services": services
    }
    
    return success_response(data=data)


@health_bp.route('/capabilities', methods=['GET'])
def capabilities():
    """
    能力探测接口
    
    返回系统支持的功能模块和能力列表
    
    GET /api/v1/system/capabilities
    
    Returns:
        {
            "trace_id": "tr_xxx",
            "data": {
                "api_version": "v1",
                "available_modules": [
                    {
                        "module_code": "F1",
                        "module_name": "客户服务管理",
                        "status": "available",
                        "features": ["智能问答", "话术生成", "质检分析"]
                    },
                    ...
                ],
                "llm_capabilities": {
                    "primary_available": true,
                    "backup_available": false,
                    "fallback_mode": false,
                    "supported_models": ["gpt-3.5-turbo"]
                },
                "features": {
                    "pagination": true,
                    "authentication": false,  # P0阶段暂未实现
                    "rate_limiting": false,   # P0阶段暂未实现
                    "soft_delete": true,
                    "multi_tenant": false     # P0阶段暂未实现
                }
            },
            "meta": {...}
        }
    """
    # 检查LLM能力
    try:
        llm_service = LLMService(current_app.config)
        llm_health = llm_service.health_check()
    except Exception as e:
        current_app.logger.error(f"LLM capability check failed: {str(e)}")
        llm_health = {
            "primary_available": False,
            "backup_available": False,
            "fallback_mode": True
        }
    
    # 五大业务模块定义
    modules = [
        {
            "module_code": "F1",
            "module_name": "客户服务管理",
            "status": "available",
            "description": "智能客服问答、话术生成、质检分析、投诉处理",
            "features": [
                "智能问答",
                "知识库管理",
                "话术生成",
                "通话质检",
                "培训内容生成",
                "投诉工单管理"
            ],
            "endpoints": [
                "/api/v1/cs/ask",
                "/api/v1/cs/knowledge",
                "/api/v1/cs/speech/generate",
                "/api/v1/cs/quality/analyze",
                "/api/v1/cs/training/generate",
                "/api/v1/cs/complaint"
            ]
        },
        {
            "module_code": "F2",
            "module_name": "高净值客户服务",
            "status": "available",
            "description": "资产配置建议、客户关怀计划、活动策划",
            "features": [
                "资产配置建议",
                "关怀计划生成",
                "活动策划",
                "触达节点查询"
            ],
            "endpoints": [
                "/api/v1/hnw/allocation",
                "/api/v1/hnw/care/plan",
                "/api/v1/hnw/event/plan",
                "/api/v1/hnw/touchpoints"
            ]
        },
        {
            "module_code": "F3",
            "module_name": "数据分析与洞察",
            "status": "available",
            "description": "客户画像分析、异常交易识别、报表生成、流失预警",
            "features": [
                "客户画像分析",
                "异常交易识别",
                "报表生成",
                "流失风险预警"
            ],
            "endpoints": [
                "/api/v1/analytics/portrait",
                "/api/v1/analytics/anomaly",
                "/api/v1/analytics/report",
                "/api/v1/analytics/churn-risk"
            ]
        },
        {
            "module_code": "F4",
            "module_name": "投教与合规",
            "status": "available",
            "description": "投教内容生成、合规培训、反洗钱检查",
            "features": [
                "投教内容生成",
                "合规培训",
                "反洗钱检查",
                "合规风险提示"
            ],
            "endpoints": [
                "/api/v1/education/content",
                "/api/v1/compliance/aml-check",
                "/api/v1/compliance/risk-tips"
            ]
        },
        {
            "module_code": "F5",
            "module_name": "市场监测与产品研究",
            "status": "available",
            "description": "舆情监控、竞品分析、市场动态",
            "features": [
                "舆情监控",
                "竞品分析",
                "市场动态简报"
            ],
            "endpoints": [
                "/api/v1/market/sentiment",
                "/api/v1/market/competitor",
                "/api/v1/market/trends"
            ]
        }
    ]
    
    data = {
        "api_version": "v1",
        "available_modules": modules,
        "llm_capabilities": {
            "primary_available": llm_health["primary_available"],
            "backup_available": llm_health["backup_available"],
            "fallback_mode": llm_health["fallback_mode"],
            "supported_models": [
                current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo')
            ],
            "timeout_seconds": current_app.config.get('LLM_TIMEOUT', 30)
        },
        "storage_capabilities": {
            "type": "json_file",
            "soft_delete": True,
            "pagination": True,
            "search": True
        },
        "features": {
            "pagination": True,
            "authentication": False,  # P0阶段暂未实现
            "rate_limiting": False,   # P0阶段暂未实现
            "soft_delete": True,
            "multi_tenant": False,    # P0阶段暂未实现
            "cors_enabled": True,
            "request_tracing": True
        }
    }
    
    return success_response(data=data)


@health_bp.route('/ping', methods=['GET'])
def ping():
    """
    简单的存活检查接口
    
    用于负载均衡器健康检查
    
    GET /api/v1/system/ping
    
    Returns:
        "pong"
    """
    return success_response(data={"status": "pong"})
