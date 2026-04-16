"""
智能问答服务模块
提供基于知识库的AI问答功能
"""

import logging
import time
from typing import Optional, List

from app.storage.kb_doc_storage import KBDocumentStorage
from app.services.llm_service import LLMService


logger = logging.getLogger(__name__)


class QAService:
    """
    智能问答服务类
    
    提供基于知识库的AI问答功能，包括：
    - 知识库搜索
    - Prompt构建
    - LLM调用
    - 响应解析
    """
    
    # 系统Prompt模板
    SYSTEM_PROMPT_TEMPLATE = """你是公募基金客户服务部的智能助手。请基于以下知识库内容回答客户问题。
如果知识库中没有相关信息，请如实告知。

【知识库参考】
{knowledge_context}

【客户问题】
{query}

请提供专业、准确、简洁的回答。如果涉及具体产品信息，请注明信息来源。"""
    
    def __init__(self, llm_service: LLMService, kb_doc_storage: KBDocumentStorage):
        """
        初始化问答服务
        
        Args:
            llm_service: LLM服务实例
            kb_doc_storage: 知识库文档存储实例
        """
        self.llm_service = llm_service
        self.kb_doc_storage = kb_doc_storage
    
    def ask(self, query: str, session_id: Optional[str] = None, 
            context: Optional[dict] = None) -> dict:
        """
        智能问答主方法
        
        流程：
        1. 搜索知识库获取相关文档
        2. 构建Prompt（系统提示 + 知识库上下文 + 用户问题）
        3. 调用LLM生成回答
        4. 返回结构化回答（含来源引用）
        
        Args:
            query: 用户问题
            session_id: 可选，会话ID
            context: 可选，额外上下文
            
        Returns:
            dict: 问答结果
            {
                "answer": str,           # AI回答
                "sources": list,         # 知识来源列表
                "confidence": float,     # 置信度 (0-1)
                "answer_source": str,    # 回答来源 (llm/knowledge/fallback)
                "response_time_ms": int, # 响应时间（毫秒）
                "session_id": str        # 会话ID
            }
        """
        start_time = time.time()
        
        try:
            # 1. 搜索知识库
            knowledge_results = self._search_knowledge(query)
            
            # 2. 构建知识库上下文
            knowledge_context = self._build_knowledge_context(knowledge_results)
            
            # 3. 构建Prompt
            prompt = self._build_prompt(query, knowledge_context)
            
            # 4. 调用LLM
            llm_result = self.llm_service.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # 5. 解析响应
            response_time_ms = int((time.time() - start_time) * 1000)
            
            result = self._parse_response(
                llm_response=llm_result,
                sources=knowledge_results,
                response_time_ms=response_time_ms
            )
            
            # 添加会话ID
            if session_id:
                result['session_id'] = session_id
            
            logger.info(f"QA completed: query='{query[:30]}...', "
                       f"source={result['answer_source']}, "
                       f"time={response_time_ms}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"QA service error: {str(e)}")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 返回降级响应
            return {
                "answer": "抱歉，系统暂时无法处理您的请求，请稍后重试。",
                "sources": [],
                "confidence": 0.0,
                "answer_source": "fallback",
                "response_time_ms": response_time_ms,
                "session_id": session_id,
                "error": str(e)
            }
    
    def _search_knowledge(self, query: str, kb_id: Optional[str] = None) -> List[dict]:
        """
        从知识库搜索相关内容
        
        Args:
            query: 查询关键词
            kb_id: 可选，指定知识库ID
            
        Returns:
            List[dict]: 相关文档列表
        """
        try:
            # 搜索文档
            results = self.kb_doc_storage.search_all(query, kb_id)
            
            # 只返回已发布的文档
            published_results = [
                doc for doc in results 
                if doc.get('status') == 'published'
            ]
            
            # 限制返回数量，优先返回最相关的
            # 这里使用简单的排序：标题匹配优先
            def relevance_score(doc):
                title = doc.get('title', '').lower()
                query_lower = query.lower()
                # 标题完全匹配得分最高
                if query_lower in title:
                    return 2
                # 标题部分匹配
                if any(word in title for word in query_lower.split()):
                    return 1
                return 0
            
            published_results.sort(key=relevance_score, reverse=True)
            
            # 最多返回5个文档
            return published_results[:5]
            
        except Exception as e:
            logger.error(f"Knowledge search error: {str(e)}")
            return []
    
    def _build_knowledge_context(self, documents: List[dict]) -> str:
        """
        构建知识库上下文
        
        将文档列表格式化为LLM可用的上下文文本
        
        Args:
            documents: 文档列表
            
        Returns:
            str: 格式化的上下文文本
        """
        if not documents:
            return "暂无相关知识库内容。"
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            title = doc.get('title', '未命名文档')
            content = doc.get('content', '')
            source = doc.get('source', '知识库')
            
            # 截断过长的内容
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            part = f"[{i}] {title}\n来源: {source}\n{content}\n"
            context_parts.append(part)
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, knowledge_context: str,
                     chat_history: Optional[List[dict]] = None) -> str:
        """
        构建Prompt模板
        
        Args:
            query: 用户问题
            knowledge_context: 知识库上下文
            chat_history: 可选，历史对话记录
            
        Returns:
            str: 完整的Prompt
        """
        # 构建基础Prompt
        prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            knowledge_context=knowledge_context,
            query=query
        )
        
        # 如果有历史对话，添加到Prompt中
        if chat_history:
            history_text = self._format_chat_history(chat_history)
            prompt = f"【历史对话】\n{history_text}\n\n{prompt}"
        
        return prompt
    
    def _format_chat_history(self, history: List[dict]) -> str:
        """
        格式化历史对话
        
        Args:
            history: 历史记录列表
            
        Returns:
            str: 格式化的历史对话文本
        """
        if not history:
            return ""
        
        # 只取最近3轮对话
        recent_history = history[-6:] if len(history) > 6 else history
        
        parts = []
        for record in recent_history:
            query = record.get('query', '')
            answer = record.get('answer', '')
            if query:
                parts.append(f"用户: {query}")
            if answer:
                parts.append(f"助手: {answer}")
        
        return "\n".join(parts)
    
    def _parse_response(self, llm_response: dict, sources: List[dict],
                       response_time_ms: int) -> dict:
        """
        解析LLM响应，提取结构化数据
        
        Args:
            llm_response: LLM返回结果
            sources: 知识来源列表
            response_time_ms: 响应时间
            
        Returns:
            dict: 结构化问答结果
        """
        content = llm_response.get('content', '').strip()
        source_type = llm_response.get('source', 'primary')
        is_fallback = llm_response.get('is_fallback', False)
        
        # 确定回答来源
        if is_fallback:
            answer_source = 'fallback'
            confidence = 0.0
        elif sources:
            answer_source = 'knowledge'
            # 根据知识库匹配程度计算置信度
            confidence = min(0.9, 0.5 + len(sources) * 0.1)
        else:
            answer_source = 'llm'
            confidence = 0.6
        
        # 格式化来源信息
        formatted_sources = []
        for doc in sources:
            formatted_sources.append({
                'id': doc.get('id'),
                'title': doc.get('title'),
                'source': doc.get('source', '知识库')
            })
        
        return {
            "answer": content,
            "sources": formatted_sources,
            "confidence": round(confidence, 2),
            "answer_source": answer_source,
            "response_time_ms": response_time_ms
        }
    
    def quick_answer(self, query: str) -> dict:
        """
        快速问答（简化版）
        
        不记录会话，直接返回答案
        
        Args:
            query: 用户问题
            
        Returns:
            dict: 问答结果
        """
        return self.ask(query, session_id=None)
