"""
培训服务模块
提供AI培训内容生成、试题生成、答案评估等功能
"""

import json
import logging

logger = logging.getLogger(__name__)


class TrainingService:
    """
    培训服务
    
    使用LLM生成培训内容和试题
    """
    
    def __init__(self, llm_service, training_storage):
        """
        初始化培训服务
        
        Args:
            llm_service: LLM服务实例
            training_storage: 培训存储实例
        """
        self.llm_service = llm_service
        self.storage = training_storage
    
    def generate_content(self, topic: str, difficulty: str = 'intermediate') -> dict:
        """
        AI生成培训内容
        
        Args:
            topic: 培训主题
            difficulty: 难度 (beginner/intermediate/advanced)
        
        Returns:
            dict: 生成的培训内容
        """
        if not topic or len(topic.strip()) < 3:
            raise ValueError("培训主题不能为空，至少需要3个字符")
        
        # 难度映射
        difficulty_map = {
            'beginner': '初级',
            'intermediate': '中级',
            'advanced': '高级'
        }
        difficulty_name = difficulty_map.get(difficulty, '中级')
        
        prompt = f"""你是公募基金培训专家。请为客服人员生成一份培训内容。

【培训主题】{topic}
【难度级别】{difficulty_name}

请生成以下内容：
1. 培训目标（3-5条）
2. 培训大纲（分章节列出）
3. 核心知识点（详细说明）
4. 案例分析（2-3个实际案例）
5. 练习题（5道选择题）

内容要求：
- 专业准确，符合基金行业规范
- 通俗易懂，适合{difficulty_name}水平学员
- 理论与实践结合

请以JSON格式返回：
{{
    "title": "培训标题",
    "objectives": ["目标1", "目标2"],
    "outline": ["章节1", "章节2"],
    "content": "核心知识点内容",
    "cases": [{{"title": "案例标题", "description": "案例描述", "solution": "解决方案"}}],
    "exercises": [{{"question": "题目", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "解析"}}]
}}
"""
        
        try:
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt="你是公募基金培训专家，擅长设计专业的客服培训课程。",
                temperature=0.7,
                max_tokens=3000
            )
            
            if not result.get('success'):
                logger.warning(f"LLM生成培训内容失败: {result.get('error')}")
                return self._get_fallback_content(topic, difficulty)
            
            content = result.get('content', '')
            parsed = self._parse_json_content(content)
            
            return {
                'title': parsed.get('title', f'{topic}培训'),
                'objectives': parsed.get('objectives', []),
                'outline': parsed.get('outline', []),
                'content': parsed.get('content', ''),
                'cases': parsed.get('cases', []),
                'exercises': parsed.get('exercises', []),
                'difficulty': difficulty,
                'source': result.get('source', 'unknown')
            }
        
        except Exception as e:
            logger.error(f"生成培训内容异常: {str(e)}")
            return self._get_fallback_content(topic, difficulty)
    
    def generate_exam(self, topic: str, question_count: int = 10) -> dict:
        """
        AI生成考核试题
        
        Args:
            topic: 考核主题
            question_count: 题目数量
        
        Returns:
            dict: 生成的试题
        """
        if not topic or len(topic.strip()) < 3:
            raise ValueError("考核主题不能为空，至少需要3个字符")
        
        # 限制题目数量
        question_count = max(5, min(50, question_count))
        
        prompt = f"""你是公募基金培训专家。请为客服人员生成一份考核试题。

【考核主题】{topic}
【题目数量】{question_count}道题

要求：
1. 题型包括：单选题（60%）、多选题（20%）、判断题（20%）
2. 难度分布：基础题（40%）、中等题（40%）、难题（20%）
3. 覆盖核心知识点
4. 每道题附带正确答案和解析

请以JSON格式返回：
{{
    "title": "考核标题",
    "duration_minutes": 30,
    "total_score": 100,
    "passing_score": 60,
    "questions": [
        {{
            "type": "single_choice",
            "question": "题目内容",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "answer": "A",
            "score": 5,
            "explanation": "答案解析"
        }}
    ]
}}

注意：
- type可以是：single_choice（单选）、multiple_choice（多选）、true_false（判断）
- multiple_choice的answer可以是数组，如["A", "B"]
- true_false不需要options，answer为"true"或"false"
"""
        
        try:
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt="你是公募基金培训专家，擅长设计专业的考核试题。",
                temperature=0.7,
                max_tokens=4000
            )
            
            if not result.get('success'):
                logger.warning(f"LLM生成试题失败: {result.get('error')}")
                return self._get_fallback_exam(topic, question_count)
            
            content = result.get('content', '')
            parsed = self._parse_json_content(content)
            
            return {
                'title': parsed.get('title', f'{topic}考核'),
                'duration_minutes': parsed.get('duration_minutes', 30),
                'total_score': parsed.get('total_score', 100),
                'passing_score': parsed.get('passing_score', 60),
                'questions': parsed.get('questions', []),
                'source': result.get('source', 'unknown')
            }
        
        except Exception as e:
            logger.error(f"生成试题异常: {str(e)}")
            return self._get_fallback_exam(topic, question_count)
    
    def evaluate_answer(self, question: str, answer: str, standard_answer: str = None) -> dict:
        """
        AI评估答案
        
        Args:
            question: 题目
            answer: 学员答案
            standard_answer: 标准答案（可选）
        
        Returns:
            dict: 评估结果
        """
        if not question or not answer:
            raise ValueError("题目和答案不能为空")
        
        context = f"""【题目】{question}
【学员答案】{answer}"""
        
        if standard_answer:
            context += f"\n【标准答案】{standard_answer}"
        
        prompt = f"""你是公募基金培训专家。请评估学员的答案。

{context}

请从以下维度评估：
1. 正确性（是否答对核心要点）
2. 完整性（是否覆盖所有要点）
3. 准确性（表述是否准确）

请以JSON格式返回：
{{
    "is_correct": true,
    "score": 85,
    "feedback": "评估反馈",
    "correct_points": ["答对的要点1", "答对的要点2"],
    "missing_points": ["遗漏的要点1"],
    "improvement_suggestions": ["改进建议1"]
}}
"""
        
        try:
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt="你是公募基金培训专家，擅长评估学员答案。",
                temperature=0.5,
                max_tokens=1500
            )
            
            if not result.get('success'):
                logger.warning(f"LLM评估答案失败: {result.get('error')}")
                return self._get_fallback_evaluation()
            
            content = result.get('content', '')
            parsed = self._parse_json_content(content)
            
            return {
                'is_correct': parsed.get('is_correct', False),
                'score': parsed.get('score', 0),
                'feedback': parsed.get('feedback', '评估完成'),
                'correct_points': parsed.get('correct_points', []),
                'missing_points': parsed.get('missing_points', []),
                'improvement_suggestions': parsed.get('improvement_suggestions', []),
                'source': result.get('source', 'unknown')
            }
        
        except Exception as e:
            logger.error(f"评估答案异常: {str(e)}")
            return self._get_fallback_evaluation()
    
    def _parse_json_content(self, content: str) -> dict:
        """解析JSON内容"""
        try:
            # 提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end + 1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("JSON解析失败")
        
        return {}
    
    def _get_fallback_content(self, topic: str, difficulty: str) -> dict:
        """获取降级培训内容"""
        return {
            'title': f'{topic}培训（系统默认）',
            'objectives': [
                '了解相关基础知识',
                '掌握基本操作流程',
                '提升服务技能'
            ],
            'outline': [
                '第一章：基础知识',
                '第二章：操作实务',
                '第三章：案例分析',
                '第四章：总结与考核'
            ],
            'content': '由于AI服务暂时不可用，显示默认培训内容。建议稍后重试获取个性化培训内容。',
            'cases': [
                {
                    'title': '典型案例',
                    'description': '这是一个示例案例',
                    'solution': '解决方案说明'
                }
            ],
            'exercises': [
                {
                    'question': '示例题目',
                    'options': ['A', 'B', 'C', 'D'],
                    'answer': 'A',
                    'explanation': '示例解析'
                }
            ],
            'difficulty': difficulty,
            'source': 'fallback'
        }
    
    def _get_fallback_exam(self, topic: str, question_count: int) -> dict:
        """获取降级试题"""
        questions = []
        for i in range(min(5, question_count)):
            questions.append({
                'type': 'single_choice',
                'question': f'示例题目{i+1}',
                'options': ['A. 选项1', 'B. 选项2', 'C. 选项3', 'D. 选项4'],
                'answer': 'A',
                'score': 10,
                'explanation': '示例解析'
            })
        
        return {
            'title': f'{topic}考核（系统默认）',
            'duration_minutes': 30,
            'total_score': 100,
            'passing_score': 60,
            'questions': questions,
            'source': 'fallback'
        }
    
    def _get_fallback_evaluation(self) -> dict:
        """获取降级评估结果"""
        return {
            'is_correct': True,
            'score': 80,
            'feedback': 'AI服务暂时不可用，显示默认评估结果。建议稍后重试获取详细评估。',
            'correct_points': ['基本正确'],
            'missing_points': [],
            'improvement_suggestions': ['建议稍后重新评估'],
            'source': 'fallback'
        }
