"""
投教内容服务模块
提供AI生成投教内容和测验的功能
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EducationService:
    """
    投教内容服务类
    
    提供以下功能：
    - AI生成投教内容
    - AI生成投教测验
    - 内容管理
    """
    
    def __init__(self, llm_service, education_storage):
        """
        初始化投教内容服务
        
        Args:
            llm_service: LLM服务实例
            education_storage: 投教内容存储实例
        """
        self.llm_service = llm_service
        self.storage = education_storage
    
    def generate_content(self, topic: str, category: str, target_audience: str, content_format: str = 'article') -> dict:
        """
        AI生成投教内容
        
        Args:
            topic: 投教主题
            category: 分类 (fund_basics/risk_management/market_knowledge/regulation)
            target_audience: 目标受众 (beginner/intermediate/advanced)
            content_format: 内容格式 (article/qa/infographic)
            
        Returns:
            dict: 生成的内容数据
        """
        # 构建提示词
        category_names = {
            'fund_basics': '基金基础知识',
            'risk_management': '风险管理',
            'market_knowledge': '市场知识',
            'regulation': '法规合规'
        }
        
        audience_names = {
            'beginner': '入门级投资者',
            'intermediate': '中级投资者',
            'advanced': '高级投资者'
        }
        
        category_name = category_names.get(category, category)
        audience_name = audience_names.get(target_audience, target_audience)
        
        system_prompt = """你是一位专业的公募基金投教内容创作专家。
请根据用户提供的主题、分类和目标受众，生成高质量的投教内容。
内容要求：
1. 专业准确，符合监管要求
2. 通俗易懂，适合目标受众理解
3. 包含风险提示
4. 结构清晰，重点突出"""
        
        prompt = f"""请生成一篇关于"{topic}"的投教内容。

分类：{category_name}
目标受众：{audience_name}
格式：{content_format}

请按以下JSON格式返回：
{{
    "title": "内容标题",
    "summary": "内容摘要（100字以内）",
    "body": "正文内容（800-1500字）",
    "key_points": ["要点1", "要点2", "要点3"],
    "risk_warnings": ["风险提示1", "风险提示2"],
    "related_concepts": ["相关概念1", "相关概念2"]
}}"""
        
        # 调用LLM生成内容
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2500
        )
        
        if not result.get('success'):
            logger.error(f"Failed to generate education content: {result.get('error')}")
            # 返回降级响应
            return self._get_fallback_content(topic, category, target_audience)
        
        # 解析生成的内容
        try:
            import json
            content_text = result.get('content', '')
            # 尝试提取JSON部分
            if '```json' in content_text:
                json_str = content_text.split('```json')[1].split('```')[0].strip()
            elif '```' in content_text:
                json_str = content_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = content_text
            
            generated_content = json.loads(json_str)
            
            return {
                'title': generated_content.get('title', f'{topic}投教内容'),
                'summary': generated_content.get('summary', ''),
                'body': generated_content.get('body', content_text),
                'key_points': generated_content.get('key_points', []),
                'risk_warnings': generated_content.get('risk_warnings', ['投资有风险，入市需谨慎']),
                'related_concepts': generated_content.get('related_concepts', []),
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to parse generated content: {str(e)}")
            return {
                'title': f'{topic}投教内容',
                'summary': '',
                'body': result.get('content', ''),
                'key_points': [],
                'risk_warnings': ['投资有风险，入市需谨慎'],
                'related_concepts': [],
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
    
    def generate_quiz(self, topic: str, difficulty: str, count: int = 5) -> dict:
        """
        AI生成投教测验
        
        Args:
            topic: 测验主题
            difficulty: 难度 (easy/medium/hard)
            count: 题目数量
            
        Returns:
            dict: 生成的测验数据
        """
        difficulty_names = {
            'easy': '简单',
            'medium': '中等',
            'hard': '困难'
        }
        
        system_prompt = """你是一位专业的投教测验出题专家。
请根据用户提供的主题和难度，生成高质量的投教测验题目。
要求：
1. 题目专业准确
2. 选项设计合理，有明确正确答案
3. 解析清晰易懂"""
        
        prompt = f"""请生成{count}道关于"{topic}"的投教测验题。
难度：{difficulty_names.get(difficulty, difficulty)}

请按以下JSON格式返回：
{{
    "questions": [
        {{
            "question": "题目内容",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "correct_answer": 0,
            "explanation": "答案解析"
        }}
    ]
}}"""
        
        # 调用LLM生成测验
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        if not result.get('success'):
            logger.error(f"Failed to generate quiz: {result.get('error')}")
            return self._get_fallback_quiz(topic, count)
        
        # 解析生成的内容
        try:
            import json
            content_text = result.get('content', '')
            # 尝试提取JSON部分
            if '```json' in content_text:
                json_str = content_text.split('```json')[1].split('```')[0].strip()
            elif '```' in content_text:
                json_str = content_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = content_text
            
            generated_quiz = json.loads(json_str)
            
            return {
                'topic': topic,
                'difficulty': difficulty,
                'questions': generated_quiz.get('questions', []),
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to parse generated quiz: {str(e)}")
            return self._get_fallback_quiz(topic, count)
    
    def save_content(self, content_data: dict, created_by: str = 'system') -> dict:
        """
        保存投教内容
        
        Args:
            content_data: 内容数据
            created_by: 创建人
            
        Returns:
            dict: 保存后的记录
        """
        content_data['created_by'] = created_by
        return self.storage.create_content(content_data)
    
    def get_content(self, content_id: str) -> Optional[dict]:
        """
        获取投教内容
        
        Args:
            content_id: 内容ID
            
        Returns:
            dict: 内容记录
        """
        return self.storage.get_content_by_id(content_id)
    
    def list_contents(self, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        """
        列表查询投教内容
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.storage.list_contents(filters, page, page_size)
    
    def _get_fallback_content(self, topic: str, category: str, target_audience: str) -> dict:
        """
        获取降级投教内容
        
        Args:
            topic: 主题
            category: 分类
            target_audience: 目标受众
            
        Returns:
            dict: 降级内容
        """
        return {
            'title': f'{topic} - 投教内容',
            'summary': f'本内容面向{target_audience}投资者，介绍{topic}相关知识。',
            'body': f'## {topic}\n\n由于AI服务暂时不可用，无法生成详细内容。请稍后重试或联系管理员。\n\n投资有风险，入市需谨慎。过往业绩不代表未来表现。',
            'key_points': [
                f'{topic}是投资中的重要概念',
                '投资前请充分了解相关风险',
                '建议根据自身风险承受能力进行投资'
            ],
            'risk_warnings': [
                '投资有风险，入市需谨慎',
                '过往业绩不代表未来表现',
                '请根据自身风险承受能力进行投资'
            ],
            'related_concepts': ['基金投资', '风险管理'],
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def _get_fallback_quiz(self, topic: str, count: int) -> dict:
        """
        获取降级测验
        
        Args:
            topic: 主题
            count: 题目数量
            
        Returns:
            dict: 降级测验
        """
        questions = []
        for i in range(min(count, 3)):
            questions.append({
                'question': f'{topic}相关测试题 {i+1}（AI服务暂时不可用，显示示例题目）',
                'options': ['选项A', '选项B', '选项C', '选项D'],
                'correct_answer': 0,
                'explanation': '由于AI服务暂时不可用，无法生成详细解析。'
            })
        
        return {
            'topic': topic,
            'difficulty': 'medium',
            'questions': questions,
            'ai_generated': False,
            'source': 'fallback'
        }
