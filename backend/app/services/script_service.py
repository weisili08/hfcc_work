"""
话术生成服务模块
提供AI话术生成功能
"""

import json
import logging

logger = logging.getLogger(__name__)


class ScriptService:
    """
    话术生成服务
    
    使用LLM生成专业客服话术
    """
    
    # 支持的场景列表
    SCENARIOS = {
        'complaint_handling': {
            'name': '投诉处理',
            'description': '处理客户投诉场景'
        },
        'product_explain': {
            'name': '产品解释',
            'description': '解释基金产品相关信息'
        },
        'retention': {
            'name': '客户挽留',
            'description': '挽留意向流失客户'
        },
        'greeting': {
            'name': '开场问候',
            'description': '电话或在线客服开场'
        },
        'closing': {
            'name': '结束语',
            'description': '服务结束时的礼貌用语'
        },
        'fee_explain': {
            'name': '费用说明',
            'description': '解释申购费、赎回费、管理费等'
        },
        'risk_disclosure': {
            'name': '风险揭示',
            'description': '提示投资风险'
        },
        'redemption_guide': {
            'name': '赎回指导',
            'description': '指导客户办理赎回'
        }
    }
    
    # 风格映射
    STYLE_MAP = {
        'professional': '专业严谨',
        'friendly': '亲切友好',
        'formal': '正式规范'
    }
    
    def __init__(self, llm_service):
        """
        初始化话术服务
        
        Args:
            llm_service: LLM服务实例
        """
        self.llm_service = llm_service
    
    def generate(self, scenario: str, context: dict = None, style: str = 'professional') -> dict:
        """
        生成客服话术
        
        Args:
            scenario: 场景（complaint_handling/product_explain/retention/greeting/closing等）
            context: 上下文信息（客户情况、产品名称等）
            style: 风格（professional/friendly/formal）
        
        Returns:
            dict: {
                'generated_script': str,
                'scenario': str,
                'suggestions': list
            }
        """
        # 参数校验
        if scenario not in self.SCENARIOS:
            valid_scenarios = ', '.join(self.SCENARIOS.keys())
            raise ValueError(f"无效的场景: {scenario}。有效场景: {valid_scenarios}")
        
        if style not in self.STYLE_MAP:
            valid_styles = ', '.join(self.STYLE_MAP.keys())
            raise ValueError(f"无效的风格: {style}。有效风格: {valid_styles}")
        
        # 构建提示词
        scenario_name = self.SCENARIOS[scenario]['name']
        style_name = self.STYLE_MAP[style]
        context_str = self._format_context(context)
        
        prompt = self._build_prompt(scenario_name, context_str, style_name)
        
        # 调用LLM生成话术
        try:
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt="你是公募基金客户服务部的话术专家，擅长生成专业、合规的客服话术。",
                temperature=0.7,
                max_tokens=1500
            )
            
            if not result.get('success'):
                logger.warning(f"LLM生成话术失败: {result.get('error')}")
                # 返回降级话术
                return self._get_fallback_script(scenario, style)
            
            content = result.get('content', '')
            
            # 解析生成的内容
            script_data = self._parse_script(content)
            
            return {
                'generated_script': script_data,
                'scenario': scenario,
                'style': style,
                'suggestions': self._generate_suggestions(scenario, context),
                'source': result.get('source', 'unknown')
            }
        
        except Exception as e:
            logger.error(f"生成话术异常: {str(e)}")
            return self._get_fallback_script(scenario, style)
    
    def get_scenarios(self) -> list:
        """
        返回所有支持的场景列表
        
        Returns:
            list: 场景列表
        """
        return [
            {
                'key': key,
                'name': value['name'],
                'description': value['description']
            }
            for key, value in self.SCENARIOS.items()
        ]
    
    def _format_context(self, context: dict) -> str:
        """格式化上下文信息"""
        if not context:
            return "无特定上下文"
        
        parts = []
        if 'customer_name' in context:
            parts.append(f"客户姓名: {context['customer_name']}")
        if 'product_name' in context:
            parts.append(f"产品名称: {context['product_name']}")
        if 'issue_description' in context:
            parts.append(f"问题描述: {context['issue_description']}")
        if 'customer_type' in context:
            parts.append(f"客户类型: {context['customer_type']}")
        if 'additional_info' in context:
            parts.append(f"补充信息: {context['additional_info']}")
        
        return '\n'.join(parts) if parts else "无特定上下文"
    
    def _build_prompt(self, scenario_name: str, context: str, style: str) -> str:
        """构建提示词模板"""
        return f"""你是公募基金客户服务部的话术专家。请根据以下场景生成专业的客服话术。

【场景】{scenario_name}
【上下文】
{context}
【风格要求】{style}

请生成：
1. 开场白
2. 核心话术（2-3段）
3. 结束语
4. 注意事项

话术要求：专业准确、语气{style}、符合金融行业合规要求。

请以以下JSON格式返回：
{{
    "opening": "开场白内容",
    "core_script": ["话术段落1", "话术段落2", "话术段落3"],
    "closing": "结束语内容",
    "notes": ["注意事项1", "注意事项2"]
}}
"""
    
    def _parse_script(self, content: str) -> dict:
        """解析LLM生成的内容"""
        try:
            # 尝试直接解析JSON
            # 先提取JSON部分（如果LLM返回了额外的文本）
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end + 1]
                data = json.loads(json_str)
                return {
                    'opening': data.get('opening', ''),
                    'core_script': data.get('core_script', []),
                    'closing': data.get('closing', ''),
                    'notes': data.get('notes', [])
                }
        except json.JSONDecodeError:
            logger.warning("无法解析JSON格式，使用原始内容")
        
        # 如果解析失败，返回原始内容
        return {
            'opening': '',
            'core_script': [content],
            'closing': '',
            'notes': []
        }
    
    def _generate_suggestions(self, scenario: str, context: dict) -> list:
        """生成使用建议"""
        suggestions = []
        
        if scenario == 'complaint_handling':
            suggestions = [
                '保持冷静，先安抚客户情绪',
                '认真倾听，不打断客户陈述',
                '记录关键信息，便于后续跟进',
                '及时反馈处理进度'
            ]
        elif scenario == 'product_explain':
            suggestions = [
                '使用通俗易懂的语言',
                '强调风险，不承诺收益',
                '根据客户风险承受能力推荐',
                '提供产品说明书供参考'
            ]
        elif scenario == 'retention':
            suggestions = [
                '了解客户流失的真实原因',
                '针对性提供解决方案',
                '强调产品长期价值',
                '保持适度联系，不过度打扰'
            ]
        elif scenario == 'risk_disclosure':
            suggestions = [
                '确保客户充分理解风险',
                '使用标准的风险提示语',
                '不淡化或回避风险',
                '建议客户阅读风险揭示书'
            ]
        else:
            suggestions = [
                '根据实际情况灵活调整话术',
                '保持专业、礼貌的服务态度',
                '注意合规要求，不违规承诺'
            ]
        
        return suggestions
    
    def _get_fallback_script(self, scenario: str, style: str) -> dict:
        """获取降级话术（当LLM不可用时）"""
        scenario_name = self.SCENARIOS.get(scenario, {}).get('name', '通用场景')
        
        return {
            'generated_script': {
                'opening': f'您好，感谢您联系公募基金客服中心。我是您的专属客服，很高兴为您服务。',
                'core_script': [
                    f'关于您咨询的{scenario_name}问题，我会尽力为您提供帮助。',
                    '由于系统暂时无法生成个性化话术，请您稍等，我将为您转接专业客服人员。',
                    '或者您也可以留下联系方式，我们会安排专人在24小时内与您联系。'
                ],
                'closing': '感谢您的理解与支持，祝您投资顺利！',
                'notes': ['当前使用系统默认话术', '建议稍后重试获取AI生成话术']
            },
            'scenario': scenario,
            'style': style,
            'suggestions': [
                '保持专业、礼貌的服务态度',
                '根据实际情况灵活调整话术',
                '注意合规要求，不违规承诺'
            ],
            'source': 'fallback'
        }
