"""
资产配置服务模块
提供AI驱动的资产配置建议生成功能
"""

import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AllocationService:
    """
    资产配置服务类
    
    基于客户画像和市场数据，利用LLM生成个性化的资产配置建议
    """
    
    # 风险等级与配置策略的映射
    RISK_ALLOCATION_TEMPLATE = {
        'conservative': {
            'equity_pct': {'min': 0, 'max': 20, 'default': 15},
            'bond_pct': {'min': 50, 'max': 70, 'default': 60},
            'money_market_pct': {'min': 20, 'max': 40, 'default': 20},
            'alternative_pct': {'min': 0, 'max': 10, 'default': 5}
        },
        'moderate': {
            'equity_pct': {'min': 30, 'max': 50, 'default': 40},
            'bond_pct': {'min': 30, 'max': 50, 'default': 40},
            'money_market_pct': {'min': 10, 'max': 20, 'default': 10},
            'alternative_pct': {'min': 5, 'max': 15, 'default': 10}
        },
        'aggressive': {
            'equity_pct': {'min': 60, 'max': 80, 'default': 70},
            'bond_pct': {'min': 10, 'max': 25, 'default': 15},
            'money_market_pct': {'min': 5, 'max': 10, 'default': 5},
            'alternative_pct': {'min': 10, 'max': 20, 'default': 10}
        }
    }
    
    # 产品推荐模板
    PRODUCT_TEMPLATES = {
        'conservative': [
            {'category': '货币基金', 'products': ['XX货币基金A', 'YY现金增利']},
            {'category': '短债基金', 'products': ['XX短债债券', 'YY中短债']},
            {'category': '纯债基金', 'products': ['XX纯债债券', 'YY信用债']}
        ],
        'moderate': [
            {'category': '混合基金', 'products': ['XX稳健增长混合', 'YY平衡配置混合']},
            {'category': '债券基金', 'products': ['XX增强债券', 'YY双债增强']},
            {'category': '指数基金', 'products': ['XX沪深300指数', 'YY中证500指数']}
        ],
        'aggressive': [
            {'category': '股票基金', 'products': ['XX成长股票', 'YY价值精选股票']},
            {'category': '行业主题', 'products': ['XX科技先锋', 'YY医疗健康']},
            {'category': 'QDII基金', 'products': ['XX全球精选', 'YY纳斯达克100']}
        ]
    }
    
    def __init__(self, llm_service):
        """
        初始化资产配置服务
        
        Args:
            llm_service: LLM服务实例
        """
        self.llm_service = llm_service
    
    def generate_allocation(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据客户画像生成资产配置建议
        
        Args:
            customer_profile: 客户画像，包含以下字段：
                - risk_level: 风险等级 (conservative/moderate/aggressive)
                - aum: 资产管理规模
                - age_range: 年龄段
                - investment_horizon: 投资期限
                - preferences: 偏好设置
        
        Returns:
            dict: 资产配置建议，包含：
                - allocation_plan: 配置计划
                - recommended_products: 推荐产品
                - risk_warnings: 风险提示
                - rationale: 配置理由
        """
        risk_level = customer_profile.get('risk_level', 'moderate')
        aum = customer_profile.get('aum', 0)
        
        # 获取基础配置模板
        base_allocation = self._get_base_allocation(risk_level, aum)
        
        # 如果LLM可用，使用AI优化配置
        if self.llm_service and self.llm_service.is_available:
            try:
                ai_allocation = self._generate_ai_allocation(customer_profile)
                if ai_allocation:
                    return ai_allocation
            except Exception as e:
                logger.warning(f"AI allocation generation failed: {e}, using fallback")
        
        # 使用本地模板生成配置
        return self._generate_fallback_allocation(customer_profile, base_allocation)
    
    def _get_base_allocation(self, risk_level: str, aum: float) -> Dict[str, int]:
        """
        获取基础配置模板
        
        Args:
            risk_level: 风险等级
            aum: 资产管理规模
        
        Returns:
            dict: 基础配置比例
        """
        template = self.RISK_ALLOCATION_TEMPLATE.get(risk_level, self.RISK_ALLOCATION_TEMPLATE['moderate'])
        
        # 根据AUM微调配置
        adjustment = 0
        if aum >= 10000000:  # 1000万以上
            adjustment = 5  # 增加权益类配置
        elif aum < 1000000:  # 100万以下
            adjustment = -5  # 降低权益类配置
        
        return {
            'equity_pct': template['equity_pct']['default'] + adjustment,
            'bond_pct': template['bond_pct']['default'] - adjustment // 2,
            'money_market_pct': template['money_market_pct']['default'],
            'alternative_pct': template['alternative_pct']['default'] - adjustment // 2
        }
    
    def _generate_ai_allocation(self, customer_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        使用LLM生成资产配置建议
        
        Args:
            customer_profile: 客户画像
        
        Returns:
            dict | None: AI生成的配置建议
        """
        system_prompt = """你是一位专业的资产配置顾问，为公募基金高净值客户提供资产配置建议。
请基于客户画像生成详细的资产配置方案，输出必须是有效的JSON格式。"""
        
        prompt = f"""请为以下高净值客户生成资产配置建议：

客户画像：
- 风险等级：{customer_profile.get('risk_level', 'moderate')}
- 资产管理规模：{customer_profile.get('aum', 0):,.0f}元
- 年龄段：{customer_profile.get('age_range', '未知')}
- 投资期限：{customer_profile.get('investment_horizon', '未知')}
- 偏好设置：{json.dumps(customer_profile.get('preferences', {}), ensure_ascii=False)}

请输出以下格式的JSON：
{{
    "allocation_plan": {{
        "equity_pct": 40,
        "bond_pct": 40,
        "money_market_pct": 10,
        "alternative_pct": 10
    }},
    "recommended_products": [
        {{
            "category": "股票基金",
            "products": ["XX成长股票", "YY价值精选"],
            "allocation_pct": 25
        }}
    ],
    "risk_warnings": ["权益类资产波动较大", "需关注市场系统性风险"],
    "rationale": "基于客户风险承受能力和投资目标..."
}}

注意：
1. 所有百分比之和必须等于100
2. 推荐产品需符合客户风险等级
3. 配置理由需具体且专业"""
        
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        if result.get('success') and not result.get('is_fallback'):
            try:
                content = result['content']
                # 提取JSON部分
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                allocation_data = json.loads(content.strip())
                allocation_data['ai_generated'] = True
                allocation_data['source'] = result.get('source', 'primary')
                return allocation_data
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI allocation response: {e}")
        
        return None
    
    def _generate_fallback_allocation(self, customer_profile: Dict[str, Any], 
                                     base_allocation: Dict[str, int]) -> Dict[str, Any]:
        """
        生成本地模板资产配置建议
        
        Args:
            customer_profile: 客户画像
            base_allocation: 基础配置
        
        Returns:
            dict: 配置建议
        """
        risk_level = customer_profile.get('risk_level', 'moderate')
        aum = customer_profile.get('aum', 0)
        
        # 获取产品推荐
        product_template = self.PRODUCT_TEMPLATES.get(risk_level, self.PRODUCT_TEMPLATES['moderate'])
        recommended_products = []
        
        for item in product_template:
            allocation_pct = 0
            if item['category'] == '货币基金' or item['category'] == '混合基金' or item['category'] == '股票基金':
                allocation_pct = base_allocation['equity_pct'] if item['category'] == '股票基金' else (
                    base_allocation['equity_pct'] if item['category'] == '混合基金' else base_allocation['money_market_pct']
                )
            elif '债' in item['category']:
                allocation_pct = base_allocation['bond_pct']
            
            recommended_products.append({
                'category': item['category'],
                'products': item['products'],
                'allocation_pct': allocation_pct
            })
        
        # 生成风险提示
        risk_warnings = self._generate_risk_warnings(risk_level, aum)
        
        # 生成配置理由
        rationale = self._generate_rationale(customer_profile, base_allocation)
        
        return {
            'allocation_plan': base_allocation,
            'recommended_products': recommended_products,
            'risk_warnings': risk_warnings,
            'rationale': rationale,
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def _generate_risk_warnings(self, risk_level: str, aum: float) -> List[str]:
        """
        生成风险提示
        
        Args:
            risk_level: 风险等级
            aum: 资产管理规模
        
        Returns:
            list: 风险提示列表
        """
        warnings = []
        
        if risk_level == 'aggressive':
            warnings.extend([
                '权益类资产配置比例较高，市场波动可能导致较大回撤',
                '建议设置止损线，控制最大亏损幅度',
                '需密切关注宏观经济和政策变化'
            ])
        elif risk_level == 'moderate':
            warnings.extend([
                '组合包含权益类资产，存在市场波动风险',
                '建议定期再平衡，维持目标配置比例'
            ])
        else:
            warnings.extend([
                '保守型配置收益率可能较低，需考虑通胀影响',
                '建议适当关注低风险收益增强机会'
            ])
        
        if aum >= 10000000:
            warnings.append('大额资金建议分批建仓，降低择时风险')
        
        return warnings
    
    def _generate_rationale(self, customer_profile: Dict[str, Any], 
                           allocation: Dict[str, int]) -> str:
        """
        生成配置理由
        
        Args:
            customer_profile: 客户画像
            allocation: 配置比例
        
        Returns:
            str: 配置理由
        """
        risk_level = customer_profile.get('risk_level', 'moderate')
        aum = customer_profile.get('aum', 0)
        horizon = customer_profile.get('investment_horizon', '中长期')
        
        rationale_parts = []
        
        # 基于风险等级的理由
        if risk_level == 'conservative':
            rationale_parts.append('基于您保守的风险偏好，本方案以债券和货币市场工具为主')
        elif risk_level == 'moderate':
            rationale_parts.append('基于您稳健的风险偏好，本方案采用股债平衡配置')
        else:
            rationale_parts.append('基于您积极的风险偏好，本方案提高权益类资产配置')
        
        # 基于AUM的理由
        if aum >= 10000000:
            rationale_parts.append(f'考虑到您{aum/10000:.0f}万的资产规模，建议适当配置另类资产以分散风险')
        
        # 基于投资期限的理由
        rationale_parts.append(f'结合您的{horizon}投资期限，该配置可平衡收益与流动性需求')
        
        return '；'.join(rationale_parts) + '。'
    
    def compare_plans(self, plan_a: Dict[str, Any], plan_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        对比两个配置方案
        
        Args:
            plan_a: 方案A
            plan_b: 方案B
        
        Returns:
            dict: 对比结果
        """
        allocation_a = plan_a.get('allocation_plan', {})
        allocation_b = plan_b.get('allocation_plan', {})
        
        # 计算差异
        differences = {}
        for key in ['equity_pct', 'bond_pct', 'money_market_pct', 'alternative_pct']:
            val_a = allocation_a.get(key, 0)
            val_b = allocation_b.get(key, 0)
            diff = val_a - val_b
            differences[key] = {
                'plan_a': val_a,
                'plan_b': val_b,
                'difference': diff,
                'significant': abs(diff) >= 10
            }
        
        # 风险等级对比
        risk_comparison = {
            'plan_a_risk': self._calculate_risk_level(allocation_a),
            'plan_b_risk': self._calculate_risk_level(allocation_b)
        }
        
        # 预期收益对比（简化估算）
        expected_return_a = self._estimate_return(allocation_a)
        expected_return_b = self._estimate_return(allocation_b)
        
        return {
            'allocation_comparison': differences,
            'risk_comparison': risk_comparison,
            'expected_return': {
                'plan_a': expected_return_a,
                'plan_b': expected_return_b,
                'difference': round(expected_return_a - expected_return_b, 2)
            },
            'recommendation': self._generate_comparison_recommendation(
                plan_a, plan_b, differences
            )
        }
    
    def _calculate_risk_level(self, allocation: Dict[str, int]) -> str:
        """
        根据配置计算风险等级
        
        Args:
            allocation: 配置比例
        
        Returns:
            str: 风险等级
        """
        equity_pct = allocation.get('equity_pct', 0)
        alternative_pct = allocation.get('alternative_pct', 0)
        
        total_risky = equity_pct + alternative_pct
        
        if total_risky >= 60:
            return 'high'
        elif total_risky >= 30:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_return(self, allocation: Dict[str, int]) -> float:
        """
        估算预期年化收益
        
        Args:
            allocation: 配置比例
        
        Returns:
            float: 预期年化收益（%）
        """
        # 简化估算：权益类8%，债券类4%，货币类2%，另类6%
        equity_return = allocation.get('equity_pct', 0) * 0.08
        bond_return = allocation.get('bond_pct', 0) * 0.04
        money_return = allocation.get('money_market_pct', 0) * 0.02
        alt_return = allocation.get('alternative_pct', 0) * 0.06
        
        return round((equity_return + bond_return + money_return + alt_return) / 100, 2)
    
    def _generate_comparison_recommendation(self, plan_a: Dict[str, Any], 
                                           plan_b: Dict[str, Any],
                                           differences: Dict[str, Any]) -> str:
        """
        生成对比推荐意见
        
        Args:
            plan_a: 方案A
            plan_b: 方案B
            differences: 差异分析
        
        Returns:
            str: 推荐意见
        """
        # 检查显著差异
        significant_diffs = [k for k, v in differences.items() if v.get('significant')]
        
        if not significant_diffs:
            return '两个方案差异不大，可根据个人偏好选择'
        
        # 分析权益类差异
        if 'equity_pct' in significant_diffs:
            diff = differences['equity_pct']['difference']
            if diff > 0:
                return '方案A权益类配置更高，适合风险承受能力较强的客户'
            else:
                return '方案B权益类配置更高，适合风险承受能力较强的客户'
        
        return '建议根据当前市场环境和客户风险偏好综合评估'
