"""
客户关怀服务模块
提供关怀计划生成、活动策划、触达话术生成等功能
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CareService:
    """
    客户关怀服务类
    
    利用LLM为高净值客户生成个性化关怀方案
    """
    
    # 关怀类型定义
    TOUCHPOINT_TYPES = {
        'birthday': {
            'name': '生日关怀',
            'timing': '生日当天或提前1-3天',
            'channels': ['电话', '微信', '短信', '礼品'],
            'priority': 'high'
        },
        'anniversary': {
            'name': '投资周年',
            'timing': '投资满周年当天',
            'channels': ['电话', '微信', '邮件'],
            'priority': 'medium'
        },
        'market_volatility': {
            'name': '市场波动关怀',
            'timing': '市场大幅波动后24小时内',
            'channels': ['电话', '微信'],
            'priority': 'high'
        },
        'redemption': {
            'name': '大额赎回关怀',
            'timing': '赎回确认后24小时内',
            'channels': ['电话'],
            'priority': 'high'
        },
        'large_redemption': {
            'name': '大额赎回预警',
            'timing': '发现大额赎回意向时',
            'channels': ['电话', '面谈'],
            'priority': 'urgent'
        },
        'no_contact': {
            'name': '久未联系',
            'timing': '超过90天未联系',
            'channels': ['电话', '微信'],
            'priority': 'medium'
        },
        'festival': {
            'name': '节日关怀',
            'timing': '节日前1-3天',
            'channels': ['微信', '短信', '礼品'],
            'priority': 'medium'
        }
    }
    
    # 活动类型模板
    EVENT_TEMPLATES = {
        'fixed_income': {
            'name': '固收策略会',
            'duration': 120,
            'suggested_venues': ['五星级酒店会议室', '私人会所', '公司路演厅'],
            'agenda_template': [
                {'time': '14:00-14:30', 'activity': '签到及茶歇', 'duration': 30},
                {'time': '14:30-15:30', 'activity': '宏观经济与债券市场展望', 'duration': 60},
                {'time': '15:30-16:00', 'activity': '固收产品策略解析', 'duration': 30},
                {'time': '16:00-16:30', 'activity': '互动交流', 'duration': 30}
            ]
        },
        'equity_roadshow': {
            'name': '权益路演',
            'duration': 150,
            'suggested_venues': ['金融中心会议室', '高端酒店宴会厅'],
            'agenda_template': [
                {'time': '14:00-14:30', 'activity': '签到', 'duration': 30},
                {'time': '14:30-15:30', 'activity': '权益市场投资机会分析', 'duration': 60},
                {'time': '15:30-16:15', 'activity': '明星基金经理分享', 'duration': 45},
                {'time': '16:15-16:45', 'activity': '问答交流', 'duration': 30}
            ]
        },
        'client_appreciation': {
            'name': '客户答谢会',
            'duration': 180,
            'suggested_venues': ['高端酒店', '高尔夫会所', '游艇俱乐部'],
            'agenda_template': [
                {'time': '17:30-18:30', 'activity': '签到及鸡尾酒会', 'duration': 60},
                {'time': '18:30-19:00', 'activity': '领导致辞', 'duration': 30},
                {'time': '19:00-20:00', 'activity': '晚宴', 'duration': 60},
                {'time': '20:00-20:30', 'activity': '文艺表演/抽奖', 'duration': 30}
            ]
        },
        'salon': {
            'name': '主题沙龙',
            'duration': 120,
            'suggested_venues': ['茶室', '书吧', '艺术中心'],
            'agenda_template': [
                {'time': '14:30-15:00', 'activity': '签到及自由交流', 'duration': 30},
                {'time': '15:00-16:00', 'activity': '主题分享', 'duration': 60},
                {'time': '16:00-16:30', 'activity': '互动讨论', 'duration': 30}
            ]
        }
    }
    
    def __init__(self, llm_service):
        """
        初始化客户关怀服务
        
        Args:
            llm_service: LLM服务实例
        """
        self.llm_service = llm_service
    
    def generate_care_plan(self, customer_info: Dict[str, Any], 
                          occasion: str) -> Dict[str, Any]:
        """
        生成关怀计划（生日、节日、投资周年等）
        
        Args:
            customer_info: 客户信息，包含：
                - name: 客户姓名
                - tier: 客户等级
                - risk_level: 风险等级
                - aum: 资产规模
                - preferences: 偏好
                - investment_date: 首次投资日期（投资周年用）
            occasion: 关怀场合 (birthday/anniversary/market_volatility/redemption/festival)
        
        Returns:
            dict: 关怀计划
        """
        touchpoint_type = self.TOUCHPOINT_TYPES.get(occasion)
        if not touchpoint_type:
            return self._generate_fallback_care_plan(customer_info, occasion)
        
        # 尝试使用LLM生成
        if self.llm_service and self.llm_service.is_available:
            try:
                ai_plan = self._generate_ai_care_plan(customer_info, occasion)
                if ai_plan:
                    return ai_plan
            except Exception as e:
                logger.warning(f"AI care plan generation failed: {e}, using fallback")
        
        return self._generate_fallback_care_plan(customer_info, occasion)
    
    def _generate_ai_care_plan(self, customer_info: Dict[str, Any], 
                               occasion: str) -> Optional[Dict[str, Any]]:
        """
        使用LLM生成关怀计划
        
        Args:
            customer_info: 客户信息
            occasion: 关怀场合
        
        Returns:
            dict | None: AI生成的关怀计划
        """
        touchpoint_type = self.TOUCHPOINT_TYPES.get(occasion, {})
        
        system_prompt = """你是一位专业的客户关系管理顾问，为高净值客户提供个性化关怀方案。
请生成专业、温暖且符合合规要求的关怀计划，输出必须是有效的JSON格式。"""
        
        prompt = f"""请为以下高净值客户生成关怀计划：

客户信息：
- 姓名：{customer_info.get('name', '客户')}
- 客户等级：{customer_info.get('tier', 'gold')}
- 风险等级：{customer_info.get('risk_level', 'moderate')}
- 资产规模：{customer_info.get('aum', 0):,.0f}元
n- 偏好：{json.dumps(customer_info.get('preferences', {}), ensure_ascii=False)}

关怀场合：{touchpoint_type.get('name', occasion)}
建议时机：{touchpoint_type.get('timing', '根据实际情况')}
建议渠道：{', '.join(touchpoint_type.get('channels', ['电话']))}

请输出以下格式的JSON：
{{
    "care_plan": {{
        "suggested_channel": "电话",
        "suggested_timing": "生日当天上午10点",
        "key_messages": ["祝福生日快乐", "感谢长期信任", "介绍最新服务"],
        "script_template": "XX先生/女士，您好！我是XX基金的客户经理XXX...",
        "accompanying_services": ["生日礼品", "专属理财报告"]
    }},
    "personalization_tips": ["客户偏好稳健投资，可提及固收产品表现", "客户关注子女教育，可适当关心"],
    "compliance_notes": ["避免承诺收益", "不得透露其他客户信息"]
}}

注意：
1. 话术需温暖专业，符合高净值客户身份
2. 必须包含合规提示
3. 根据客户等级调整服务标准"""
        
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1500
        )
        
        if result.get('success') and not result.get('is_fallback'):
            try:
                content = result['content']
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                plan_data = json.loads(content.strip())
                plan_data['touchpoint_type'] = occasion
                plan_data['ai_generated'] = True
                plan_data['source'] = result.get('source', 'primary')
                return plan_data
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI care plan response: {e}")
        
        return None
    
    def _generate_fallback_care_plan(self, customer_info: Dict[str, Any], 
                                     occasion: str) -> Dict[str, Any]:
        """
        生成本地模板关怀计划
        
        Args:
            customer_info: 客户信息
            occasion: 关怀场合
        
        Returns:
            dict: 关怀计划
        """
        touchpoint_type = self.TOUCHPOINT_TYPES.get(occasion, {})
        tier = customer_info.get('tier', 'gold')
        name = customer_info.get('name', '客户')
        
        # 根据客户等级调整服务
        if tier == 'diamond':
            services = ['专属礼品', '一对一理财报告', 'VIP活动邀请']
            channel = '电话（优先）或面谈'
        elif tier == 'platinum':
            services = ['精美礼品', '季度投资报告']
            channel = '电话或微信'
        else:
            services = ['电子贺卡', '投资资讯']
            channel = '微信或短信'
        
        # 根据场合生成话术模板
        script_templates = {
            'birthday': f'{name}先生/女士，您好！我是XX基金的客户经理XXX。今天是您的生日，我代表公司祝您生日快乐，身体健康，阖家幸福！感谢您一直以来对我们的信任与支持。',
            'anniversary': f'{name}先生/女士，您好！今天是你投资我们产品的第X周年。感谢您长期以来的信任，我们为您准备了一份投资回顾报告...',
            'market_volatility': f'{name}先生/女士，您好！近期市场波动较大，关注到您的持仓情况，特意致电向您说明当前市场情况及我们的观点...',
            'redemption': f'{name}先生/女士，您好！注意到您近期有赎回操作，想了解是否对我们的服务有任何建议，或者有什么可以帮助您的...',
            'festival': f'{name}先生/女士，您好！值此佳节之际，祝您节日快乐！感谢您一直以来的支持...'
        }
        
        return {
            'touchpoint_type': occasion,
            'care_plan': {
                'suggested_channel': channel,
                'suggested_timing': touchpoint_type.get('timing', '根据实际情况'),
                'key_messages': [
                    f'表达{touchpoint_type.get("name", "关怀")}祝福',
                    '感谢客户信任与支持',
                    '介绍相关服务或产品（如适用）'
                ],
                'script_template': script_templates.get(occasion, f'{name}先生/女士，您好！我是XX基金的客户经理XXX...'),
                'accompanying_services': services
            },
            'personalization_tips': [
                f'客户等级为{tier}，需提供对应标准的服务',
                '根据客户持仓情况调整沟通重点'
            ],
            'compliance_notes': [
                '不得承诺投资收益',
                '不得透露其他客户信息',
                '产品推介需匹配客户风险等级'
            ],
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def plan_event(self, event_type: str, target_customers: List[Dict[str, Any]], 
                   budget: float) -> Dict[str, Any]:
        """
        AI策划客户活动
        
        Args:
            event_type: 活动类型 (fixed_income/equity_roadshow/client_appreciation/salon)
            target_customers: 目标客户列表
            budget: 预算金额
        
        Returns:
            dict: 活动策划方案
        """
        template = self.EVENT_TEMPLATES.get(event_type)
        if not template:
            return {'error': f'Unknown event type: {event_type}'}
        
        # 尝试使用LLM生成
        if self.llm_service and self.llm_service.is_available:
            try:
                ai_plan = self._generate_ai_event_plan(event_type, target_customers, budget)
                if ai_plan:
                    return ai_plan
            except Exception as e:
                logger.warning(f"AI event plan generation failed: {e}, using fallback")
        
        return self._generate_fallback_event_plan(event_type, target_customers, budget)
    
    def _generate_ai_event_plan(self, event_type: str, 
                                target_customers: List[Dict[str, Any]], 
                                budget: float) -> Optional[Dict[str, Any]]:
        """
        使用LLM生成活动策划
        
        Args:
            event_type: 活动类型
            target_customers: 目标客户
            budget: 预算
        
        Returns:
            dict | None: AI生成的活动策划
        """
        template = self.EVENT_TEMPLATES.get(event_type, {})
        
        system_prompt = """你是一位专业的活动策划专家，为高净值客户策划专属活动。
请生成详细的活动策划方案，输出必须是有效的JSON格式。"""
        
        prompt = f"""请策划一场高净值客户活动：

活动类型：{template.get('name', event_type)}
目标客户数：{len(target_customers)}人
预算：{budget:,.0f}元

目标客户画像：
{json.dumps([{'tier': c.get('tier'), 'aum': c.get('aum')} for c in target_customers[:3]], ensure_ascii=False)}

请输出以下格式的JSON：
{{
    "event_proposal": {{
        "theme": "活动主题",
        "date_suggestion": "建议日期及时间",
        "venue_suggestion": "场地建议",
        "agenda": [
            {{"time": "14:00-14:30", "activity": "签到", "duration": 30}}
        ],
        "materials_checklist": ["签到表", "宣传册", "伴手礼"],
        "budget_estimate": {{
            "total": {budget},
            "breakdown": [
                {{"item": "场地", "amount": 50000}},
                {{"item": "餐饮", "amount": 30000}}
            ]
        }}
    }},
    "target_guests": [
        {{"tier": "diamond", "expected_count": 10, "invitation_priority": "high"}}
    ],
    "invitation_template": {{
        "subject": "邀请函主题",
        "body": "邀请函正文"
    }}
}}

注意：
1. 活动主题需高端大气，符合高净值客户品味
2. 预算分配需合理
3. 流程安排需紧凑且舒适"""
        
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2000
        )
        
        if result.get('success') and not result.get('is_fallback'):
            try:
                content = result['content']
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                plan_data = json.loads(content.strip())
                plan_data['ai_generated'] = True
                plan_data['source'] = result.get('source', 'primary')
                return plan_data
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI event plan response: {e}")
        
        return None
    
    def _generate_fallback_event_plan(self, event_type: str, 
                                      target_customers: List[Dict[str, Any]], 
                                      budget: float) -> Dict[str, Any]:
        """
        生成本地模板活动策划
        
        Args:
            event_type: 活动类型
            target_customers: 目标客户
            budget: 预算
        
        Returns:
            dict: 活动策划方案
        """
        template = self.EVENT_TEMPLATES.get(event_type, {})
        
        # 计算预算分配
        attendee_count = len(target_customers)
        budget_per_person = budget / attendee_count if attendee_count > 0 else 0
        
        # 预算分配建议
        if budget_per_person >= 2000:
            venue_budget = budget * 0.4
            catering_budget = budget * 0.3
            material_budget = budget * 0.2
            other_budget = budget * 0.1
        elif budget_per_person >= 1000:
            venue_budget = budget * 0.35
            catering_budget = budget * 0.35
            material_budget = budget * 0.2
            other_budget = budget * 0.1
        else:
            venue_budget = budget * 0.3
            catering_budget = budget * 0.4
            material_budget = budget * 0.2
            other_budget = budget * 0.1
        
        # 统计客户等级分布
        tier_counts = {}
        for customer in target_customers:
            tier = customer.get('tier', 'gold')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        target_guests = []
        for tier, count in tier_counts.items():
            target_guests.append({
                'tier': tier,
                'expected_count': count,
                'invitation_priority': 'high' if tier == 'diamond' else ('medium' if tier == 'platinum' else 'normal')
            })
        
        return {
            'event_proposal': {
                'theme': f'{template.get("name", "客户活动")}——洞察市场·共赢未来',
                'date_suggestion': '建议工作日下午14:00-17:00或周末下午',
                'venue_suggestion': template.get('suggested_venues', ['公司会议室'])[0],
                'agenda': template.get('agenda_template', []),
                'materials_checklist': [
                    '签到表及名牌',
                    '公司宣传册',
                    '产品资料',
                    '伴手礼',
                    '投影设备',
                    '茶歇点心'
                ],
                'budget_estimate': {
                    'total': budget,
                    'breakdown': [
                        {'item': '场地租赁', 'amount': round(venue_budget)},
                        {'item': '餐饮茶歇', 'amount': round(catering_budget)},
                        {'item': '物料制作', 'amount': round(material_budget)},
                        {'item': '其他费用', 'amount': round(other_budget)}
                    ]
                }
            },
            'target_guests': target_guests,
            'invitation_template': {
                'subject': f'诚挚邀请 | {template.get("name", "专属活动")}',
                'body': f'''尊敬的贵宾：

诚挚邀请您参加我们精心筹备的{template.get("name", "客户活动")}。

活动时间：[具体日期]
活动地点：[具体地点]

届时将有资深投资专家为您深度解析市场趋势，
并有机会与志同道合的投资人交流分享。

期待您的莅临！

XX基金 敬邀'''
            },
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def generate_touchpoint_script(self, customer_info: Dict[str, Any], 
                                   trigger_event: str) -> Dict[str, Any]:
        """
        生成触达话术（大额赎回、久未联系等）
        
        Args:
            customer_info: 客户信息
            trigger_event: 触发事件 (large_redemption/no_contact/market_volatility)
        
        Returns:
            dict: 触达话术
        """
        touchpoint_type = self.TOUCHPOINT_TYPES.get(trigger_event)
        if not touchpoint_type:
            return {'error': f'Unknown trigger event: {trigger_event}'}
        
        # 尝试使用LLM生成
        if self.llm_service and self.llm_service.is_available:
            try:
                ai_script = self._generate_ai_touchpoint_script(customer_info, trigger_event)
                if ai_script:
                    return ai_script
            except Exception as e:
                logger.warning(f"AI touchpoint script generation failed: {e}, using fallback")
        
        return self._generate_fallback_touchpoint_script(customer_info, trigger_event)
    
    def _generate_ai_touchpoint_script(self, customer_info: Dict[str, Any], 
                                       trigger_event: str) -> Optional[Dict[str, Any]]:
        """
        使用LLM生成触达话术
        
        Args:
            customer_info: 客户信息
            trigger_event: 触发事件
        
        Returns:
            dict | None: AI生成的话术
        """
        touchpoint_type = self.TOUCHPOINT_TYPES.get(trigger_event, {})
        
        system_prompt = """你是一位资深的客户关系管理专家，擅长为高净值客户设计沟通话术。
请生成专业、得体且有温度的触达话术，输出必须是有效的JSON格式。"""
        
        prompt = f"""请为以下场景生成触达话术：

客户信息：
- 姓名：{customer_info.get('name', '客户')}
- 等级：{customer_info.get('tier', 'gold')}
- 风险等级：{customer_info.get('risk_level', 'moderate')}
- AUM：{customer_info.get('aum', 0):,.0f}元

触发事件：{touchpoint_type.get('name', trigger_event)}
优先级：{touchpoint_type.get('priority', 'medium')}
建议渠道：{', '.join(touchpoint_type.get('channels', ['电话']))}

请输出以下格式的JSON：
{{
    "script": {{
        "opening": "开场白",
        "body": "核心内容",
        "closing": "结束语",
        "handling_objections": ["异议处理话术1", "异议处理话术2"]
    }},
    "key_points": ["沟通要点1", "沟通要点2"],
    "timing_suggestion": "最佳触达时间",
    "follow_up_actions": ["后续行动1", "后续行动2"],
    "compliance_reminders": ["合规提醒1", "合规提醒2"]
}}

注意：
1. 话术需专业得体，符合高净值客户沟通习惯
2. 需包含异议处理方案
3. 必须包含合规提醒"""
        
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1500
        )
        
        if result.get('success') and not result.get('is_fallback'):
            try:
                content = result['content']
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                script_data = json.loads(content.strip())
                script_data['trigger_event'] = trigger_event
                script_data['ai_generated'] = True
                script_data['source'] = result.get('source', 'primary')
                return script_data
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI touchpoint script response: {e}")
        
        return None
    
    def _generate_fallback_touchpoint_script(self, customer_info: Dict[str, Any], 
                                             trigger_event: str) -> Dict[str, Any]:
        """
        生成本地模板触达话术
        
        Args:
            customer_info: 客户信息
            trigger_event: 触发事件
        
        Returns:
            dict: 触达话术
        """
        name = customer_info.get('name', '客户')
        tier = customer_info.get('tier', 'gold')
        
        # 根据触发事件生成话术
        scripts = {
            'large_redemption': {
                'opening': f'{name}先生/女士，您好！我是XX基金的客户经理XXX。注意到您近期有大额赎回意向，想了解一下是否有什么可以帮助您的？',
                'body': '首先，我完全理解您可能有资金安排的需要。同时，也想了解一下，是否对我们的服务或产品表现有什么不满意的地方？您的反馈对我们非常重要。',
                'closing': '无论如何，我们都会尊重您的决定。如果您需要，我可以为您安排一次详细的持仓分析，帮助您做出最优决策。',
                'handling_objections': [
                    '客户：收益不理想。回应：我理解您的感受，近期市场确实波动较大。从历史数据来看，长期持有...',
                    '客户：需要用钱。回应：理解，如果确实需要资金，我们可以探讨部分赎回或更灵活的方案。'
                ]
            },
            'no_contact': {
                'opening': f'{name}先生/女士，您好！我是XX基金的客户经理XXX。好久不见了，特意致电问候一下。',
                'body': '最近市场有一些新的变化，不知道您是否有关注到？另外，也想了解一下您目前的持仓情况，看看是否有需要调整的地方。',
                'closing': '如果您有时间，我们可以安排一次详细的资产检视。祝您生活愉快！',
                'handling_objections': [
                    '客户：最近很忙。回应：理解，那我先不打扰您。稍后我会发一份最新的市场观点到您邮箱，您方便时看看。',
                    '客户：没什么需要。回应：好的，那我定期为您发送市场资讯，有需要随时联系我。'
                ]
            },
            'market_volatility': {
                'opening': f'{name}先生/女士，您好！我是XX基金的客户经理XXX。近期市场波动较大，特意致电向您说明一下情况。',
                'body': '首先，请不要过于担心。市场的短期波动是正常的，您的组合配置是基于您的风险承受能力设计的。从历史经验来看...',
                'closing': '如果您有任何疑问或担忧，随时可以联系我。我们会持续关注市场动态，及时与您沟通。',
                'handling_objections': [
                    '客户：要不要赎回？回应：建议您从长期投资的角度考虑，短期波动不应影响长期决策。我们可以一起分析一下...',
                    '客户：还能涨回来吗？回应：历史数据显示，优质资产长期看都有较好的回报。关键是保持理性，避免追涨杀跌。'
                ]
            }
        }
        
        default_script = {
            'opening': f'{name}先生/女士，您好！我是XX基金的客户经理XXX。',
            'body': '今天联系您是想了解一下您的投资情况，看看是否有可以帮助您的地方。',
            'closing': '感谢您的时间，如有任何需要随时联系我。祝您生活愉快！',
            'handling_objections': ['客户：不需要。回应：好的，那我先不打扰您，有需要随时联系。']
        }
        
        script = scripts.get(trigger_event, default_script)
        
        return {
            'trigger_event': trigger_event,
            'script': script,
            'key_points': [
                '表达关心和重视',
                '了解客户需求和顾虑',
                '提供专业建议（如适用）'
            ],
            'timing_suggestion': '工作日上午10点-11点或下午2点-4点',
            'follow_up_actions': [
                '记录沟通内容',
                '根据客户反馈安排后续服务',
                '定期跟进'
            ],
            'compliance_reminders': [
                '不得承诺投资收益',
                '不得诱导客户进行交易',
                '尊重客户自主决策权'
            ],
            'ai_generated': False,
            'source': 'fallback'
        }
