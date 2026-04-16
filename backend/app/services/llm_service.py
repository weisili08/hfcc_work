"""
LLM服务模块
提供大语言模型API的调用封装
支持主备LLM切换、降级响应、重试机制
"""

import time
import logging
import requests
from typing import Optional


logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM服务类
    
    提供统一的LLM调用接口，支持：
    - OpenAI兼容API调用
    - 指数退避重试（最多3次）
    - 降级响应（当API不可用时）
    - 调用日志记录
    """
    
    def __init__(self, config: dict):
        """
        初始化LLM服务
        
        Args:
            config: 配置字典，包含以下键：
                - LLM_API_KEY: 主LLM API密钥
                - LLM_API_URL: 主LLM API地址
                - LLM_MODEL: 主LLM模型名称
                - LLM_TIMEOUT: 请求超时时间（秒）
                - LLM_BACKUP_API_KEY: 备用LLM API密钥（可选）
                - LLM_BACKUP_API_URL: 备用LLM API地址（可选）
                - LLM_BACKUP_MODEL: 备用LLM模型名称（可选）
        """
        # 主LLM配置
        self.api_key = config.get('LLM_API_KEY', '')
        self.api_url = config.get('LLM_API_URL', 'https://api.openai.com/v1')
        self.model = config.get('LLM_MODEL', 'gpt-3.5-turbo')
        self.timeout = config.get('LLM_TIMEOUT', 30)
        
        # 备用LLM配置
        self.backup_api_key = config.get('LLM_BACKUP_API_KEY', '')
        self.backup_api_url = config.get('LLM_BACKUP_API_URL', '')
        self.backup_model = config.get('LLM_BACKUP_MODEL', '')
        
        # 标准化API URL（确保以/chat/completions结尾）
        self.api_url = self._normalize_api_url(self.api_url)
        if self.backup_api_url:
            self.backup_api_url = self._normalize_api_url(self.backup_api_url)
    
    def _normalize_api_url(self, url: str) -> str:
        """
        标准化API URL
        
        确保URL以/chat/completions结尾
        
        Args:
            url: 原始URL
        
        Returns:
            str: 标准化后的URL
        """
        url = url.rstrip('/')
        if not url.endswith('/chat/completions'):
            if '/v1' in url:
                url = f"{url}/chat/completions"
            else:
                url = f"{url}/v1/chat/completions"
        return url
    
    @property
    def is_available(self) -> bool:
        """
        检查LLM服务是否可用
        
        判断依据：主API key已配置
        
        Returns:
            bool: 服务是否可用
        """
        return bool(self.api_key and self.api_key.strip())
    
    @property
    def is_backup_available(self) -> bool:
        """
        检查备用LLM服务是否可用
        
        Returns:
            bool: 备用服务是否可用
        """
        return bool(
            self.backup_api_key and 
            self.backup_api_key.strip() and
            self.backup_api_url and
            self.backup_api_url.strip()
        )
    
    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> dict:
        """
        调用LLM聊天接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]
            temperature: 温度参数（0-2）
            max_tokens: 最大生成token数
            **kwargs: 其他参数（如top_p, frequency_penalty等）
        
        Returns:
            dict: 调用结果
            {
                "content": str,       # 生成的内容
                "model": str,         # 使用的模型
                "usage": dict,        # token使用统计
                "success": bool,      # 是否成功
                "source": str,        # 响应来源：primary/backup/fallback
                "response_time_ms": int  # 响应时间（毫秒）
            }
        """
        # 构建请求payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        return self._call_api_with_fallback(payload)
    
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> dict:
        """
        简化的生成接口
        
        将prompt包装为messages格式调用chat方法
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            **kwargs: 其他参数
        
        Returns:
            dict: 调用结果（同chat方法）
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, **kwargs)
    
    def _call_api_with_fallback(self, payload: dict) -> dict:
        """
        调用API，支持主备切换和降级
        
        调用顺序：主LLM -> 备用LLM -> 降级响应
        
        Args:
            payload: API请求payload
        
        Returns:
            dict: 调用结果
        """
        start_time = time.time()
        
        # 1. 尝试主LLM
        if self.is_available:
            result = self._call_api(
                self.api_url, 
                self.api_key, 
                self.model,
                payload
            )
            if result['success']:
                result['source'] = 'primary'
                result['response_time_ms'] = int((time.time() - start_time) * 1000)
                return result
            logger.warning(f"Primary LLM failed: {result.get('error')}")
        
        # 2. 尝试备用LLM
        if self.is_backup_available:
            backup_payload = payload.copy()
            backup_payload['model'] = self.backup_model or payload.get('model')
            
            result = self._call_api(
                self.backup_api_url,
                self.backup_api_key,
                self.backup_model,
                backup_payload
            )
            if result['success']:
                result['source'] = 'backup'
                result['response_time_ms'] = int((time.time() - start_time) * 1000)
                return result
            logger.warning(f"Backup LLM failed: {result.get('error')}")
        
        # 3. 返回降级响应
        logger.warning("All LLM services unavailable, returning fallback response")
        fallback = self._get_fallback_response(payload.get('messages', []))
        fallback['response_time_ms'] = int((time.time() - start_time) * 1000)
        return fallback
    
    def _call_api(self, api_url: str, api_key: str, model: str, payload: dict) -> dict:
        """
        实际API调用，带重试和超时
        
        使用指数退避重试策略：1s, 2s, 4s
        
        Args:
            api_url: API地址
            api_key: API密钥
            model: 模型名称
            payload: 请求payload
        
        Returns:
            dict: 调用结果
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        max_retries = 3
        retry_delays = [1, 2, 4]  # 指数退避：1s, 2s, 4s
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 记录调用日志
                prompt_length = sum(len(m.get('content', '')) for m in payload.get('messages', []))
                logger.info(
                    f"LLM API call - Model: {model}, "
                    f"Prompt length: {prompt_length}, "
                    f"Status: {response.status_code}, "
                    f"Attempt: {attempt + 1}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get('choices', [])
                    
                    if choices:
                        content = choices[0].get('message', {}).get('content', '')
                        return {
                            "content": content,
                            "model": data.get('model', model),
                            "usage": data.get('usage', {}),
                            "success": True,
                            "source": "primary",
                            "response_time_ms": 0  # 由上层填充
                        }
                    else:
                        return {
                            "content": "",
                            "model": model,
                            "usage": {},
                            "success": False,
                            "error": "Empty response from LLM",
                            "source": "primary"
                        }
                
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"LLM API error: {error_msg}")
                    
                    # 如果是4xx错误，不重试
                    if 400 <= response.status_code < 500:
                        return {
                            "content": "",
                            "model": model,
                            "usage": {},
                            "success": False,
                            "error": error_msg,
                            "source": "primary"
                        }
                    
                    # 5xx错误，继续重试
                    if attempt < max_retries - 1:
                        delay = retry_delays[attempt]
                        logger.info(f"Retrying in {delay}s...")
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.Timeout:
                logger.warning(f"LLM API timeout (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    time.sleep(delay)
                    continue
                return {
                    "content": "",
                    "model": model,
                    "usage": {},
                    "success": False,
                    "error": "Request timeout",
                    "source": "primary"
                }
            
            except requests.exceptions.RequestException as e:
                logger.error(f"LLM API request error: {str(e)}")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    time.sleep(delay)
                    continue
                return {
                    "content": "",
                    "model": model,
                    "usage": {},
                    "success": False,
                    "error": str(e),
                    "source": "primary"
                }
            
            except Exception as e:
                logger.error(f"Unexpected error calling LLM: {str(e)}")
                return {
                    "content": "",
                    "model": model,
                    "usage": {},
                    "success": False,
                    "error": str(e),
                    "source": "primary"
                }
        
        # 所有重试都失败
        return {
            "content": "",
            "model": model,
            "usage": {},
            "success": False,
            "error": "Max retries exceeded",
            "source": "primary"
        }
    
    def _get_fallback_response(self, messages: list) -> dict:
        """
        获取降级响应
        
        当所有LLM服务都不可用时返回预设回复
        
        Args:
            messages: 原始消息列表
        
        Returns:
            dict: 降级响应
        """
        # 提取用户最后一条消息用于生成上下文相关的降级回复
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        # 生成降级回复
        fallback_content = self._generate_fallback_content(user_message)
        
        logger.info(f"Returning fallback response for prompt: {user_message[:50]}...")
        
        return {
            "content": fallback_content,
            "model": "fallback",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "success": True,  # 降级响应标记为成功，但标识为fallback
            "source": "fallback",
            "is_fallback": True,
            "response_time_ms": 0
        }
    
    def _generate_fallback_content(self, user_message: str) -> str:
        """
        生成降级回复内容
        
        根据用户消息类型返回不同的预设回复
        
        Args:
            user_message: 用户消息
        
        Returns:
            str: 降级回复内容
        """
        # 简单的关键词匹配，返回预设回复
        message_lower = user_message.lower()
        
        # 问候类
        if any(word in message_lower for word in ['你好', '您好', 'hello', 'hi']):
            return "您好！我是AI客服助手。目前智能服务暂时不可用，请稍后重试或联系人工客服。"
        
        # 产品咨询类
        if any(word in message_lower for word in ['产品', '基金', '收益', '净值', '申购', '赎回']):
            return "感谢您的咨询。关于产品相关问题，建议您：1）查看产品说明书；2）登录官网查询最新净值；3）联系人工客服获取详细解答。"
        
        # 投诉类
        if any(word in message_lower for word in ['投诉', '不满', '问题', '错误']):
            return "非常抱歉给您带来不便。您的反馈已记录，我们会尽快处理。紧急问题请拨打客服热线：400-xxx-xxxx。"
        
        # 默认回复
        return "感谢您的咨询。当前智能服务暂时不可用，建议您：1）稍后重试；2）查看知识库常见问题；3）联系人工客服获取帮助。"
    
    def health_check(self) -> dict:
        """
        健康检查
        
        检查LLM服务的可用状态
        
        Returns:
            dict: 健康状态
            {
                "primary_available": bool,
                "backup_available": bool,
                "fallback_mode": bool
            }
        """
        return {
            "primary_available": self.is_available,
            "backup_available": self.is_backup_available,
            "fallback_mode": not self.is_available and not self.is_backup_available
        }
