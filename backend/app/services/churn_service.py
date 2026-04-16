"""
流失预警服务模块
提供AI驱动的客户流失预测和挽留建议功能
"""

import json
import logging

logger = logging.getLogger(__name__)


class ChurnService:
    """
    流失预警服务类
    
    提供客户流失风险预测、挽留建议生成等功能
    """
    
    def __init__(self, llm_service, churn_storage, profile_storage=None):
        """
        初始化流失预警服务
        
        Args:
            llm_service: LLM服务实例
            churn_storage: 流失风险存储实例
            profile_storage: 客户画像存储实例（可选）
        """
        self.llm_service = llm_service
        self.churn_storage = churn_storage
        self.profile_storage = profile_storage
    
    def predict(self, customer_data: dict) -> dict:
        """
        预测流失风险
        
        基于客户数据预测流失风险等级和分数
        
        Args:
            customer_data: 客户数据，包含交易记录、行为数据、服务记录等
        
        Returns:
            dict: 预测结果，包含风险分数、等级、风险因素等
        """
        try:
            # 首先进行规则评分
            rule_score = self._calculate_rule_based_score(customer_data)
            
            # 使用AI进行深度分析
            system_prompt = """你是一位专业的客户流失预测分析师，擅长识别客户流失风险信号。
请基于客户数据，分析其流失风险并生成预测结果。

请评估以下维度：
1. 交易活跃度变化
2. 资产规模变化趋势
3. 投诉/服务请求频率
4. 产品赎回情况
5. 互动频率下降

请以JSON格式返回结果：
{
    "risk_score": 0-100,
    "risk_level": "critical/high/medium/low",
    "risk_factors": ["风险因素1", "风险因素2", ...],
    "confidence": "high/medium/low"
}"""
            
            customer_json = json.dumps(customer_data, ensure_ascii=False, indent=2)
            prompt = f"请预测以下客户的流失风险：\n\n{customer_json}"
            
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            if not result.get('success'):
                logger.warning(f"LLM流失预测失败: {result.get('error')}")
                return rule_score
            
            # 解析AI分析结果
            content = result.get('content', '')
            try:
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    ai_result = json.loads(json_str)
                else:
                    ai_result = json.loads(content)
                
                # 合并规则和AI结果（取较高风险）
                ai_score = ai_result.get('risk_score', 0)
                rule_risk_score = rule_score.get('risk_score', 0)
                
                final_score = max(ai_score, rule_risk_score)
                
                # 确定风险等级
                if final_score >= 80:
                    risk_level = 'critical'
                elif final_score >= 60:
                    risk_level = 'high'
                elif final_score >= 40:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                # 合并风险因素
                risk_factors = list(set(
                    ai_result.get('risk_factors', []) + 
                    rule_score.get('risk_factors', [])
                ))
                
                return {
                    'risk_score': final_score,
                    'risk_level': risk_level,
                    'risk_factors': risk_factors,
                    'ai_confidence': ai_result.get('confidence', 'medium'),
                    'source': 'ai_prediction'
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"解析AI预测结果失败: {e}")
                return rule_score
                
        except Exception as e:
            logger.error(f"流失预测服务异常: {e}")
            return {'risk_score': 50, 'risk_level': 'medium', 'risk_factors': ['系统分析异常'], 'source': 'fallback'}
    
    def generate_retention_plan(self, customer_id: str) -> dict:
        """
        生成挽留建议
        
        基于客户流失风险记录生成个性化挽留方案
        
        Args:
            customer_id: 客户ID
        
        Returns:
            dict: 挽留建议
        """
        # 获取流失风险记录
        risk_record = self.churn_storage.get_by_customer(customer_id)
        
        if not risk_record:
            return {'error': '未找到该客户的流失风险记录'}
        
        # 获取客户画像（如果有）
        profile = None
        if self.profile_storage:
            # 尝试查找对应的画像
            profiles = self.profile_storage.list(filters={'customer_id': customer_id}, page_size=1)
            if profiles.get('items'):
                profile = profiles['items'][0]
        
        try:
            system_prompt = """你是一位资深的客户关系管理专家，擅长制定客户挽留策略。
请基于客户的流失风险信息，生成个性化的挽留建议方案。

请提供以下内容：
1. 挽留策略概述
2. 具体行动建议（3-5条）
3. 推荐沟通话术
4. 可提供的服务或优惠
5. 后续跟进计划

请以JSON格式返回结果。"""
            
            context = {
                'risk_record': risk_record,
                'profile': profile
            }
            context_json = json.dumps(context, ensure_ascii=False, indent=2)
            prompt = f"请为以下客户生成挽留建议方案：\n\n{context_json}"
            
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=1200
            )
            
            if not result.get('success'):
                return self._get_fallback_retention_plan(risk_record, profile)
            
            content = result.get('content', '')
            
            # 尝试解析JSON
            try:
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    plan = json.loads(json_str)
                else:
                    plan = {'plan_content': content}
                
                # 更新风险记录
                suggestions = plan.get('action_suggestions', plan.get('具体行动建议', []))
                if isinstance(suggestions, list):
                    self.churn_storage.update_retention_plan(risk_record['id'], suggestions)
                
                plan['customer_id'] = customer_id
                plan['risk_level'] = risk_record.get('risk_level')
                return plan
                
            except json.JSONDecodeError:
                suggestions = [content[:200]] if len(content) > 200 else [content]
                self.churn_storage.update_retention_plan(risk_record['id'], suggestions)
                return {
                    'customer_id': customer_id,
                    'risk_level': risk_record.get('risk_level'),
                    'plan_content': content,
                    'source': 'ai_generation'
                }
                
        except Exception as e:
            logger.error(f"生成挽留计划异常: {e}")
            return self._get_fallback_retention_plan(risk_record, profile)
    
    def create_risk_record(self, customer_id: str, customer_name: str, 
                          customer_data: dict = None) -> dict:
        """
        创建流失风险记录
        
        Args:
            customer_id: 客户ID
            customer_name: 客户姓名
            customer_data: 客户数据（用于预测）
        
        Returns:
            dict: 创建的风险记录
        """
        # 如果提供了客户数据，进行预测
        if customer_data:
            prediction = self.predict(customer_data)
        else:
            # 默认中等风险
            prediction = {
                'risk_score': 50,
                'risk_level': 'medium',
                'risk_factors': ['缺乏近期数据'],
                'source': 'default'
            }
        
        record = self.churn_storage.create_risk_record(
            customer_id=customer_id,
            customer_name=customer_name,
            risk_score=prediction.get('risk_score', 50),
            risk_level=prediction.get('risk_level', 'medium'),
            risk_factors=prediction.get('risk_factors', [])
        )
        
        record['prediction'] = prediction
        return record
    
    def update_risk_status(self, risk_id: str, status: str) -> dict:
        """
        更新流失风险状态
        
        Args:
            risk_id: 风险记录ID
            status: 新状态
        
        Returns:
            dict: 更新后的记录
        """
        return self.churn_storage.update_status(risk_id, status)
    
    def get_high_risk_summary(self) -> dict:
        """
        获取高风险客户汇总
        
        Returns:
            dict: 高风险客户统计
        """
        high_risk = self.churn_storage.get_high_risk_customers(threshold=70)
        stats = self.churn_storage.get_statistics()
        
        return {
            'high_risk_count': len(high_risk),
            'high_risk_customers': [
                {
                    'id': c['id'],
                    'customer_id': c['customer_id'],
                    'customer_name': c['customer_name'],
                    'risk_score': c['risk_score'],
                    'risk_level': c['risk_level'],
                    'risk_factors': c.get('risk_factors', [])
                }
                for c in high_risk[:10]  # 只返回前10个
            ],
            'statistics': stats
        }
    
    def _calculate_rule_based_score(self, customer_data: dict) -> dict:
        """
        基于规则计算流失风险分数
        """
        score = 0
        risk_factors = []
        
        # 规则1: 近期无交易
        days_since_last = customer_data.get('days_since_last_transaction', 0)
        if days_since_last >= 90:
            score += 30
            risk_factors.append(f'{days_since_last}天未发生交易')
        elif days_since_last >= 60:
            score += 20
            risk_factors.append('超过60天未交易')
        elif days_since_last >= 30:
            score += 10
            risk_factors.append('超过30天未交易')
        
        # 规则2: 资产规模下降
        aum_change = customer_data.get('aum_change_percent', 0)
        if aum_change <= -50:
            score += 30
            risk_factors.append('资产规模下降超过50%')
        elif aum_change <= -30:
            score += 20
            risk_factors.append('资产规模下降超过30%')
        elif aum_change <= -10:
            score += 10
            risk_factors.append('资产规模下降超过10%')
        
        # 规则3: 近期投诉
        recent_complaints = customer_data.get('recent_complaint_count', 0)
        if recent_complaints >= 3:
            score += 25
            risk_factors.append(f'近期投诉{recent_complaints}次')
        elif recent_complaints >= 1:
            score += 15
            risk_factors.append('近期有投诉记录')
        
        # 规则4: 大额赎回
        recent_redemption = customer_data.get('recent_redemption_amount', 0)
        current_aum = customer_data.get('current_aum', 1)
        if current_aum > 0 and recent_redemption / current_aum >= 0.5:
            score += 25
            risk_factors.append('近期大额赎回')
        
        # 规则5: 登录/互动频率下降
        login_decline = customer_data.get('login_frequency_decline', False)
        if login_decline:
            score += 15
            risk_factors.append('登录频率明显下降')
        
        # 确定风险等级
        if score >= 70:
            risk_level = 'high'
        elif score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': min(100, score),
            'risk_level': risk_level,
            'risk_factors': risk_factors if risk_factors else ['暂无明确风险信号'],
            'source': 'rule_calculation'
        }
    
    def _get_fallback_retention_plan(self, risk_record: dict, profile: dict = None) -> dict:
        """
        获取降级挽留建议
        """
        risk_level = risk_record.get('risk_level', 'medium')
        
        plans = {
            'critical': {
                'strategy_summary': '该客户流失风险极高，需要立即采取紧急挽留措施。',
                'action_suggestions': [
                    '安排高级客户经理立即联系',
                    '了解客户不满的具体原因',
                    '提供专属服务方案或费率优惠',
                    '邀请参加VIP客户活动'
                ],
                'communication_script': '您好，我们注意到您近期可能对我们的服务有些疑虑，我想亲自了解一下您的情况，看看我们如何能更好地为您服务。',
                'offers': ['费率减免', '专属理财顾问', '优先服务通道'],
                'follow_up_plan': '每日跟进，直至风险解除'
            },
            'high': {
                'strategy_summary': '该客户存在明显流失风险，需要主动干预。',
                'action_suggestions': [
                    '客户经理主动联系关怀',
                    '推送个性化产品推荐',
                    '邀请参加投资者教育活动',
                    '提供市场分析报告'
                ],
                'communication_script': '您好，我们为您准备了一些个性化的投资建议，希望能帮助您更好地实现投资目标。',
                'offers': ['免费投资咨询', '定制化报告'],
                'follow_up_plan': '每周跟进，持续4周'
            },
            'medium': {
                'strategy_summary': '该客户需要关注，通过常规维护提升满意度。',
                'action_suggestions': [
                    '定期发送市场资讯',
                    '邀请参加线上讲座',
                    '推送适合的产品信息'
                ],
                'communication_script': '您好，我们有一些新的投资机会想与您分享，不知道您是否有兴趣了解？',
                'offers': ['投资资讯服务'],
                'follow_up_plan': '每月跟进'
            },
            'low': {
                'strategy_summary': '该客户目前稳定，维持正常服务即可。',
                'action_suggestions': [
                    '保持常规服务品质',
                    '定期关怀问候'
                ],
                'communication_script': '感谢您的信任，如有任何需求请随时联系我们。',
                'offers': [],
                'follow_up_plan': '按常规周期维护'
            }
        }
        
        plan = plans.get(risk_level, plans['medium']).copy()
        plan['customer_id'] = risk_record.get('customer_id')
        plan['risk_level'] = risk_level
        plan['source'] = 'fallback'
        
        return plan
