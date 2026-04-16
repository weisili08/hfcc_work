"""
质检服务模块
提供AI质检分析功能
"""

import json
import logging
import re

logger = logging.getLogger(__name__)


class QualityService:
    """
    质检服务
    
    使用LLM分析客服通话质量
    """
    
    def __init__(self, llm_service, quality_storage):
        """
        初始化质检服务
        
        Args:
            llm_service: LLM服务实例
            quality_storage: 质检存储实例
        """
        self.llm_service = llm_service
        self.storage = quality_storage
    
    def analyze(self, call_content: str, agent_name: str = None) -> dict:
        """
        AI质检分析
        
        1. 调用LLM分析通话内容
        2. 评分（态度、专业度、合规性、问题解决）
        3. 识别问题点
        4. 生成改进建议
        
        Args:
            call_content: 通话内容
            agent_name: 客服姓名（可选）
        
        Returns:
            dict: {
                'overall_score': int,
                'scores': dict,
                'issues': list,
                'suggestions': list
            }
        """
        if not call_content or len(call_content.strip()) < 10:
            raise ValueError("通话内容太短，无法进行分析")
        
        # 构建提示词
        prompt = self._build_analysis_prompt(call_content)
        
        try:
            # 调用LLM
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt="你是公募基金客服质量检查专家，擅长评估客服通话质量。",
                temperature=0.3,  # 较低温度以获得更稳定的评分
                max_tokens=2000
            )
            
            if not result.get('success'):
                logger.warning(f"LLM质检分析失败: {result.get('error')}")
                return self._get_fallback_analysis()
            
            content = result.get('content', '')
            
            # 解析分析结果
            analysis = self._parse_analysis_result(content)
            analysis['source'] = result.get('source', 'unknown')
            
            return analysis
        
        except Exception as e:
            logger.error(f"质检分析异常: {str(e)}")
            return self._get_fallback_analysis()
    
    def get_statistics(self, date_range: dict = None) -> dict:
        """
        质检统计（平均分、评分分布、常见问题TOP5）
        
        Args:
            date_range: 日期范围
        
        Returns:
            dict: 统计数据
        """
        return self.storage.get_statistics(date_range)
    
    def create_check_record(self, agent_name: str, call_date: str, 
                           call_duration: int, call_content: str) -> dict:
        """
        创建质检记录
        
        Args:
            agent_name: 客服姓名
            call_date: 通话日期
            call_duration: 通话时长（秒）
            call_content: 通话内容
        
        Returns:
            dict: 创建的记录
        """
        record = {
            'agent_name': agent_name,
            'call_date': call_date,
            'call_duration': call_duration,
            'call_content': call_content,
            'status': 'pending',
            'overall_score': None,
            'scores': {},
            'issues': [],
            'suggestions': [],
            'analyzed_by': None
        }
        
        return self.storage.create(record)
    
    def analyze_and_save(self, check_id: str) -> dict:
        """
        对已有记录进行AI分析并保存结果
        
        Args:
            check_id: 质检记录ID
        
        Returns:
            dict: 更新后的记录
        """
        record = self.storage.get(check_id)
        if not record:
            raise ValueError("质检记录不存在")
        
        # 更新状态为分析中
        self.storage.update_status(check_id, 'analyzing')
        
        # 进行分析
        call_content = record.get('call_content', '')
        analysis = self.analyze(call_content, record.get('agent_name'))
        
        # 保存分析结果
        result = self.storage.update_analysis_result(check_id, {
            'overall_score': analysis.get('overall_score'),
            'scores': analysis.get('scores'),
            'issues': analysis.get('issues'),
            'suggestions': analysis.get('suggestions'),
            'analyzed_by': 'AI'
        })
        
        return result
    
    def _build_analysis_prompt(self, call_content: str) -> str:
        """构建质检分析提示词"""
        return f"""你是公募基金客服质量检查专家。请对以下客服通话内容进行质量评估。

【通话内容】
{call_content}

请从以下维度评分（0-100分）并给出分析：
1. 服务态度（是否礼貌、耐心、积极）
2. 专业度（产品知识是否准确、解释是否清晰）
3. 合规性（是否存在违规承诺、误导性信息）
4. 问题解决（是否有效解决客户问题）

请以JSON格式返回：
{{
  "overall_score": 85,
  "scores": {{"attitude": 90, "professionalism": 85, "compliance": 80, "problem_solving": 85}},
  "issues": ["问题1描述", "问题2描述"],
  "suggestions": ["建议1", "建议2"]
}}

注意：
- 评分要客观公正，基于实际表现
- issues和suggestions要具体、可操作
- 如果没有明显问题，issues可以为空数组
"""
    
    def _parse_analysis_result(self, content: str) -> dict:
        """解析LLM返回的分析结果"""
        try:
            # 提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end + 1]
                data = json.loads(json_str)
                
                # 验证和规范化数据
                overall_score = self._validate_score(data.get('overall_score'))
                scores = data.get('scores', {})
                
                return {
                    'overall_score': overall_score,
                    'scores': {
                        'attitude': self._validate_score(scores.get('attitude')),
                        'professionalism': self._validate_score(scores.get('professionalism')),
                        'compliance': self._validate_score(scores.get('compliance')),
                        'problem_solving': self._validate_score(scores.get('problem_solving'))
                    },
                    'issues': data.get('issues', []),
                    'suggestions': data.get('suggestions', [])
                }
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {str(e)}")
        except Exception as e:
            logger.warning(f"解析分析结果失败: {str(e)}")
        
        # 解析失败，尝试正则提取
        return self._extract_scores_by_regex(content)
    
    def _validate_score(self, score) -> int:
        """验证并规范化评分"""
        try:
            score = int(score)
            return max(0, min(100, score))
        except (TypeError, ValueError):
            return 0
    
    def _extract_scores_by_regex(self, content: str) -> dict:
        """使用正则表达式提取评分（备用方案）"""
        # 尝试提取overall_score
        overall_match = re.search(r'overall_score["\']?\s*[:=]\s*(\d+)', content)
        overall_score = int(overall_match.group(1)) if overall_match else 75
        
        # 尝试提取各维度评分
        scores = {}
        dimensions = ['attitude', 'professionalism', 'compliance', 'problem_solving']
        for dim in dimensions:
            pattern = rf'{dim}["\']?\s*[:=]\s*(\d+)'
            match = re.search(pattern, content, re.IGNORECASE)
            scores[dim] = int(match.group(1)) if match else overall_score
        
        return {
            'overall_score': overall_score,
            'scores': scores,
            'issues': ['解析结果时可能遗漏部分信息'],
            'suggestions': ['建议重新分析以获得更准确结果']
        }
    
    def _get_fallback_analysis(self) -> dict:
        """获取降级分析结果（当LLM不可用时）"""
        return {
            'overall_score': 75,
            'scores': {
                'attitude': 80,
                'professionalism': 75,
                'compliance': 75,
                'problem_solving': 70
            },
            'issues': ['AI服务暂时不可用，使用默认评分'],
            'suggestions': [
                '建议稍后重新进行AI质检分析',
                '可转人工质检以获得更准确评估'
            ],
            'source': 'fallback'
        }
