"""
客户画像服务模块
提供AI驱动的客户画像分析功能
"""

import json
import logging

logger = logging.getLogger(__name__)


class ProfileService:
    """
    客户画像服务类
    
    提供客户画像的AI分析、相似客户查找、洞察生成等功能
    """
    
    def __init__(self, llm_service, profile_storage):
        """
        初始化客户画像服务
        
        Args:
            llm_service: LLM服务实例
            profile_storage: 客户画像存储实例
        """
        self.llm_service = llm_service
        self.profile_storage = profile_storage
    
    def analyze_profile(self, customer_data: dict) -> dict:
        """
        AI分析客户画像，生成标签和洞察
        
        Args:
            customer_data: 客户数据，包含基本信息、交易记录、行为数据等
        
        Returns:
            dict: 分析结果，包含画像标签、价值分层、风险等级等
        """
        try:
            # 构建分析提示词
            system_prompt = """你是一位专业的基金客户分析师，擅长根据客户数据生成精准的客户画像分析。
请基于提供的客户数据，生成结构化的分析结果，包括：
1. 客户标签（行为特征、偏好特征）
2. 价值分层（high/medium/low）
3. 风险等级（保守型/稳健型/平衡型/成长型/进取型）
4. 产品偏好
5. 活跃度评分（0-100）
6. 忠诚度评分（0-100）
7. 分析摘要

请以JSON格式返回结果，格式如下：
{
    "behavior_tags": ["标签1", "标签2", ...],
    "value_tier": "high|medium|low",
    "risk_level": "保守型|稳健型|平衡型|成长型|进取型",
    "product_preferences": ["产品类型1", "产品类型2", ...],
    "activity_score": 85,
    "loyalty_score": 78,
    "analysis_summary": "客户分析摘要..."
}"""
            
            # 将客户数据转换为JSON字符串
            customer_json = json.dumps(customer_data, ensure_ascii=False, indent=2)
            
            prompt = f"请分析以下客户数据并生成客户画像：\n\n{customer_json}"
            
            # 调用LLM进行分析
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            if not result.get('success'):
                logger.error(f"LLM分析失败: {result.get('error')}")
                return self._get_fallback_analysis(customer_data)
            
            # 解析LLM返回的JSON
            content = result.get('content', '')
            
            # 尝试提取JSON部分
            try:
                # 查找JSON内容
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    analysis = json.loads(json_str)
                else:
                    analysis = json.loads(content)
                
                # 验证必要字段
                required_fields = ['behavior_tags', 'value_tier', 'risk_level', 
                                  'activity_score', 'loyalty_score', 'analysis_summary']
                for field in required_fields:
                    if field not in analysis:
                        analysis[field] = self._get_default_value(field)
                
                analysis['ai_analysis_source'] = result.get('source', 'unknown')
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"解析LLM返回结果失败: {e}, content: {content[:200]}")
                return self._get_fallback_analysis(customer_data)
                
        except Exception as e:
            logger.error(f"客户画像分析异常: {e}")
            return self._get_fallback_analysis(customer_data)
    
    def find_similar(self, profile_id: str, top_n: int = 5) -> list:
        """
        查找相似客户
        
        Args:
            profile_id: 参考客户画像ID
            top_n: 返回数量
        
        Returns:
            list: 相似客户列表
        """
        return self.profile_storage.find_similar_profiles(profile_id, top_n)
    
    def get_insights(self, profile_id: str) -> dict:
        """
        获取客户洞察
        
        基于客户画像数据生成深度洞察和建议
        
        Args:
            profile_id: 客户画像ID
        
        Returns:
            dict: 客户洞察
        """
        profile = self.profile_storage.get(profile_id)
        if not profile:
            return {'error': '客户画像不存在'}
        
        try:
            system_prompt = """你是一位资深的基金客户顾问，擅长基于客户画像提供个性化的深度洞察和服务建议。
请基于客户画像数据，生成以下内容的分析：
1. 客户特征总结
2. 潜在需求分析
3. 服务建议
4. 产品推荐方向
5. 风险提醒

请以JSON格式返回结果。"""
            
            profile_json = json.dumps(profile, ensure_ascii=False, indent=2)
            prompt = f"请基于以下客户画像生成深度洞察：\n\n{profile_json}"
            
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=1500
            )
            
            if not result.get('success'):
                return self._get_fallback_insights(profile)
            
            content = result.get('content', '')
            
            # 尝试解析JSON
            try:
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    insights = json.loads(json_str)
                else:
                    insights = {'analysis': content}
                
                insights['profile_id'] = profile_id
                insights['customer_name'] = profile.get('customer_name')
                return insights
                
            except json.JSONDecodeError:
                return {
                    'profile_id': profile_id,
                    'customer_name': profile.get('customer_name'),
                    'analysis': content,
                    'summary': profile.get('analysis_summary', '')
                }
                
        except Exception as e:
            logger.error(f"生成客户洞察异常: {e}")
            return self._get_fallback_insights(profile)
    
    def create_profile(self, customer_data: dict, auto_analyze: bool = True) -> dict:
        """
        创建客户画像
        
        Args:
            customer_data: 客户基础数据
            auto_analyze: 是否自动进行AI分析
        
        Returns:
            dict: 创建的客户画像
        """
        if auto_analyze:
            analysis = self.analyze_profile(customer_data)
            customer_data.update(analysis)
        
        return self.profile_storage.create(customer_data)
    
    def update_profile_analysis(self, profile_id: str) -> dict:
        """
        重新分析客户画像
        
        Args:
            profile_id: 客户画像ID
        
        Returns:
            dict: 更新后的画像
        """
        profile = self.profile_storage.get(profile_id)
        if not profile:
            return {'error': '客户画像不存在'}
        
        # 重新分析
        analysis = self.analyze_profile(profile)
        
        # 更新存储
        updates = {
            'behavior_tags': analysis.get('behavior_tags', []),
            'value_tier': analysis.get('value_tier', 'medium'),
            'risk_level': analysis.get('risk_level', '稳健型'),
            'product_preferences': analysis.get('product_preferences', []),
            'activity_score': analysis.get('activity_score', 50),
            'loyalty_score': analysis.get('loyalty_score', 50),
            'analysis_summary': analysis.get('analysis_summary', '')
        }
        
        return self.profile_storage.update(profile_id, updates)
    
    def _get_fallback_analysis(self, customer_data: dict) -> dict:
        """
        获取降级分析结果
        
        当LLM不可用时返回默认分析
        """
        # 基于简单规则生成分析
        aum = customer_data.get('aum', 0)
        transaction_count = customer_data.get('transaction_count', 0)
        
        # 价值分层
        if aum >= 1000000:
            value_tier = 'high'
        elif aum >= 100000:
            value_tier = 'medium'
        else:
            value_tier = 'low'
        
        # 活跃度评分
        activity_score = min(100, transaction_count * 5 + 30)
        
        # 忠诚度评分（基于持有时间等）
        loyalty_score = 60
        
        return {
            'behavior_tags': ['普通客户', '待激活'],
            'value_tier': value_tier,
            'risk_level': '稳健型',
            'product_preferences': ['货币基金', '债券基金'],
            'activity_score': activity_score,
            'loyalty_score': loyalty_score,
            'analysis_summary': '基于规则生成的默认客户画像分析。该客户为普通投资者，建议进一步了解其投资偏好和风险承受能力。',
            'ai_analysis_source': 'fallback'
        }
    
    def _get_fallback_insights(self, profile: dict) -> dict:
        """
        获取降级洞察结果
        """
        value_tier = profile.get('value_tier', 'medium')
        risk_level = profile.get('risk_level', '稳健型')
        
        tier_advice = {
            'high': '重点维护客户，提供专属理财顾问服务',
            'medium': '潜力客户，可通过增值服务提升粘性',
            'low': '基础服务客户，关注成本效益'
        }
        
        return {
            'profile_id': profile.get('id'),
            'customer_name': profile.get('customer_name'),
            'characteristics': f"该客户为{value_tier}价值客户，风险偏好为{risk_level}。",
            'needs_analysis': '需要进一步了解客户的投资目标和资金流动性需求。',
            'service_suggestions': tier_advice.get(value_tier, '提供标准化服务'),
            'product_recommendations': ['货币基金', '债券基金'],
            'risk_warnings': ['市场波动风险', '流动性风险'],
            'ai_analysis_source': 'fallback'
        }
    
    def _get_default_value(self, field: str):
        """获取字段默认值"""
        defaults = {
            'behavior_tags': [],
            'value_tier': 'medium',
            'risk_level': '稳健型',
            'product_preferences': [],
            'activity_score': 50,
            'loyalty_score': 50,
            'analysis_summary': ''
        }
        return defaults.get(field)
