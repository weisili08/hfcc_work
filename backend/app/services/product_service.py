"""
产品研究服务模块
提供AI产品分析和竞品对比功能
"""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class ProductService:
    """
    产品研究服务类
    
    提供以下功能：
    - AI产品分析
    - 竞品对比分析
    - 产品推荐
    """
    
    def __init__(self, llm_service, product_storage):
        """
        初始化产品研究服务
        
        Args:
            llm_service: LLM服务实例
            product_storage: 产品分析存储实例
        """
        self.llm_service = llm_service
        self.storage = product_storage
    
    def analyze(self, product_info: dict) -> dict:
        """
        AI产品分析
        
        Args:
            product_info: 产品信息
            {
                'product_name': '产品名称',
                'product_type': '产品类型',
                'company': '基金公司',
                'fund_code': '基金代码',
                'establishment_date': '成立日期',
                'fund_size': '基金规模',
                'investment_strategy': '投资策略'
            }
            
        Returns:
            dict: 分析结果
        """
        system_prompt = """你是一位专业的基金研究分析师。
请对提供的基金产品进行深度分析，包括：
1. 产品基本信息分析
2. 业绩表现评估
3. 风险指标分析
4. 投资策略评价
5. 适合投资者类型建议
6. 综合评价和推荐建议"""
        
        prompt = f"""请分析以下基金产品：

产品名称：{product_info.get('product_name', '未知')}
产品类型：{product_info.get('product_type', '未知')}
基金公司：{product_info.get('company', '未知')}
基金代码：{product_info.get('fund_code', '未知')}
成立日期：{product_info.get('establishment_date', '未知')}
基金规模：{product_info.get('fund_size', '未知')}
投资策略：{product_info.get('investment_strategy', '未知')}

请按以下JSON格式返回分析结果：
{{
    "analysis_summary": "分析摘要",
    "performance_analysis": {{
        "overall_rating": "优秀/良好/一般/较差",
        "strengths": ["优势1", "优势2"],
        "weaknesses": ["劣势1", "劣势2"]
    }},
    "risk_assessment": {{
        "risk_level": "高/中/低",
        "risk_factors": ["风险因子1", "风险因子2"],
        "risk_warnings": ["风险提示1", "风险提示2"]
    }},
    "suitable_investors": ["适合投资者类型1", "适合投资者类型2"],
    "investment_recommendation": "投资建议",
    "overall_score": 85
}}"""
        
        # 调用LLM进行分析
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2000
        )
        
        if not result.get('success'):
            logger.error(f"Failed to analyze product: {result.get('error')}")
            return self._get_fallback_analysis(product_info)
        
        # 解析分析结果
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
            
            analysis = json.loads(json_str)
            
            return {
                'product_name': product_info.get('product_name'),
                'product_type': product_info.get('product_type'),
                'company': product_info.get('company'),
                'analysis_content': analysis,
                'performance_data': {
                    'overall_score': analysis.get('overall_score', 0),
                    'rating': analysis.get('performance_analysis', {}).get('overall_rating', '一般')
                },
                'risk_metrics': {
                    'risk_level': analysis.get('risk_assessment', {}).get('risk_level', '中'),
                    'risk_factors': analysis.get('risk_assessment', {}).get('risk_factors', [])
                },
                'recommendation': analysis.get('investment_recommendation', ''),
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to parse product analysis: {str(e)}")
            return self._get_fallback_analysis(product_info)
    
    def compare(self, products: list) -> dict:
        """
        竞品对比分析
        
        Args:
            products: 产品列表，每个产品包含product_name, product_type, company等
            
        Returns:
            dict: 对比分析结果
        """
        if len(products) < 2:
            return {
                'error': '至少需要2个产品进行对比',
                'success': False
            }
        
        system_prompt = """你是一位专业的基金对比分析专家。
请对提供的多个基金产品进行对比分析，包括：
1. 各维度对比（业绩、风险、费用等）
2. 优劣势分析
3. 差异化特点
4. 适用场景建议
5. 综合推荐排序"""
        
        products_str = '\n\n'.join([
            f"产品{i+1}:\n" + '\n'.join([f"  {k}: {v}" for k, v in p.items()])
            for i, p in enumerate(products)
        ])
        
        prompt = f"""请对比分析以下基金产品：

{products_str}

请按以下JSON格式返回对比分析结果：
{{
    "comparison_matrix": {{
        "dimensions": ["业绩", "风险", "费用", "规模"],
        "products": [
            {{"name": "产品1名称", "scores": {{"业绩": 85, "风险": 70, "费用": 80, "规模": 90}}}},
            {{"name": "产品2名称", "scores": {{"业绩": 75, "风险": 80, "费用": 75, "规模": 85}}}}
        ]
    }},
    "ai_analysis": {{
        "summary": "对比分析摘要",
        "competitive_advantages": ["竞争优势1", "竞争优势2"],
        "competitive_disadvantages": ["竞争劣势1", "竞争劣势2"],
        "differentiation": "差异化分析",
        "market_positioning": "市场定位分析"
    }},
    "ranking": [
        {{"rank": 1, "product_name": "产品1", "reason": "推荐理由"}},
        {{"rank": 2, "product_name": "产品2", "reason": "推荐理由"}}
    ],
    "recommendations": {{
        "conservative": "保守型投资者推荐",
        "balanced": "平衡型投资者推荐",
        "aggressive": "激进型投资者推荐"
    }}
}}"""
        
        # 调用LLM进行对比分析
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2500
        )
        
        if not result.get('success'):
            logger.error(f"Failed to compare products: {result.get('error')}")
            return self._get_fallback_comparison(products)
        
        # 解析分析结果
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
            
            comparison = json.loads(json_str)
            
            return {
                'comparison_matrix': comparison.get('comparison_matrix', {}),
                'ai_analysis': comparison.get('ai_analysis', {}),
                'ranking': comparison.get('ranking', []),
                'recommendations': comparison.get('recommendations', {}),
                'compared_products': [p.get('product_name') for p in products],
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to parse product comparison: {str(e)}")
            return self._get_fallback_comparison(products)
    
    def recommend(self, customer_profile: dict) -> dict:
        """
        产品推荐
        
        Args:
            customer_profile: 客户画像
            {
                'risk_level': '风险等级C1-C5',
                'investment_goal': '投资目标',
                'time_horizon': '投资期限',
                'aum': '资产规模'
            }
            
        Returns:
            dict: 推荐结果
        """
        risk_level = customer_profile.get('risk_level', 'C3')
        investment_goal = customer_profile.get('investment_goal', '稳健增值')
        time_horizon = customer_profile.get('time_horizon', '中长期')
        
        # 根据风险等级确定产品类型
        risk_product_mapping = {
            'C1': ['money_market'],
            'C2': ['money_market', 'bond_fund'],
            'C3': ['bond_fund', 'mixed'],
            'C4': ['mixed', 'equity_fund'],
            'C5': ['equity_fund', 'mixed']
        }
        
        suitable_types = risk_product_mapping.get(risk_level, ['mixed'])
        
        system_prompt = """你是一位专业的基金推荐顾问。
请根据客户画像推荐合适的基金产品，包括：
1. 推荐理由
2. 产品特点
3. 风险提示
4. 配置建议"""
        
        prompt = f"""请为以下客户推荐基金产品：

客户画像：
- 风险等级：{risk_level}
- 投资目标：{investment_goal}
- 投资期限：{time_horizon}
- 适合产品类型：{', '.join(suitable_types)}

请按以下JSON格式返回推荐结果：
{{
    "recommendations": [
        {{
            "product_type": "产品类型",
            "allocation_percentage": 40,
            "reason": "推荐理由",
            "suggested_products": ["建议产品1", "建议产品2"],
            "risk_warnings": ["风险提示1"]
        }}
    ],
    "portfolio_summary": "组合配置摘要",
    "expected_return_range": "预期收益区间",
    "risk_level": "组合风险等级",
    "disclaimer": "免责声明"
}}"""
        
        # 调用LLM生成推荐
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=2000
        )
        
        if not result.get('success'):
            logger.error(f"Failed to generate recommendation: {result.get('error')}")
            return self._get_fallback_recommendation(customer_profile)
        
        # 解析推荐结果
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
            
            recommendation = json.loads(json_str)
            
            return {
                'customer_profile': customer_profile,
                'recommendations': recommendation.get('recommendations', []),
                'portfolio_summary': recommendation.get('portfolio_summary', ''),
                'expected_return_range': recommendation.get('expected_return_range', ''),
                'risk_level': recommendation.get('risk_level', risk_level),
                'disclaimer': recommendation.get('disclaimer', '投资有风险，入市需谨慎'),
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to parse recommendation: {str(e)}")
            return self._get_fallback_recommendation(customer_profile)
    
    def save_analysis(self, analysis_data: dict, created_by: str = 'system') -> dict:
        """
        保存产品分析
        
        Args:
            analysis_data: 分析数据
            created_by: 创建人
            
        Returns:
            dict: 保存后的记录
        """
        analysis_data['created_by'] = created_by
        return self.storage.create_analysis(analysis_data)
    
    def get_analysis(self, analysis_id: str) -> Optional[dict]:
        """
        获取产品分析
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            dict: 分析记录
        """
        return self.storage.get_analysis_by_id(analysis_id)
    
    def list_analyses(self, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        """
        列表查询产品分析
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.storage.list_analyses(filters, page, page_size)
    
    def _get_fallback_analysis(self, product_info: dict) -> dict:
        """
        获取降级产品分析
        
        Args:
            product_info: 产品信息
            
        Returns:
            dict: 降级分析
        """
        return {
            'product_name': product_info.get('product_name'),
            'product_type': product_info.get('product_type'),
            'company': product_info.get('company'),
            'analysis_content': {
                'analysis_summary': 'AI服务暂时不可用，无法生成详细分析',
                'performance_analysis': {
                    'overall_rating': '一般',
                    'strengths': ['无法获取'],
                    'weaknesses': ['无法获取']
                },
                'risk_assessment': {
                    'risk_level': '中',
                    'risk_factors': ['市场风险', '流动性风险'],
                    'risk_warnings': ['投资有风险，入市需谨慎']
                },
                'suitable_investors': ['风险承受能力匹配的投资者'],
                'investment_recommendation': '建议详细了解产品信息后再做投资决策',
                'overall_score': 0
            },
            'performance_data': {'overall_score': 0, 'rating': '一般'},
            'risk_metrics': {'risk_level': '中', 'risk_factors': ['市场风险']},
            'recommendation': 'AI服务暂时不可用，请稍后重试',
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def _get_fallback_comparison(self, products: list) -> dict:
        """
        获取降级产品对比
        
        Args:
            products: 产品列表
            
        Returns:
            dict: 降级对比
        """
        return {
            'comparison_matrix': {
                'dimensions': ['业绩', '风险', '费用'],
                'products': [
                    {'name': p.get('product_name', f'产品{i+1}'), 'scores': {}}
                    for i, p in enumerate(products)
                ]
            },
            'ai_analysis': {
                'summary': 'AI服务暂时不可用，无法生成详细对比分析',
                'competitive_advantages': [],
                'competitive_disadvantages': [],
                'differentiation': '无法获取',
                'market_positioning': '无法获取'
            },
            'ranking': [
                {'rank': i+1, 'product_name': p.get('product_name', f'产品{i+1}'), 'reason': 'AI服务不可用'}
                for i, p in enumerate(products)
            ],
            'recommendations': {
                'conservative': 'AI服务暂时不可用',
                'balanced': 'AI服务暂时不可用',
                'aggressive': 'AI服务暂时不可用'
            },
            'compared_products': [p.get('product_name') for p in products],
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def _get_fallback_recommendation(self, customer_profile: dict) -> dict:
        """
        获取降级产品推荐
        
        Args:
            customer_profile: 客户画像
            
        Returns:
            dict: 降级推荐
        """
        risk_level = customer_profile.get('risk_level', 'C3')
        
        risk_mapping = {
            'C1': ['货币基金'],
            'C2': ['货币基金', '债券基金'],
            'C3': ['债券基金', '混合基金'],
            'C4': ['混合基金', '股票基金'],
            'C5': ['股票基金', '混合基金']
        }
        
        suggested_types = risk_mapping.get(risk_level, ['混合基金'])
        
        return {
            'customer_profile': customer_profile,
            'recommendations': [
                {
                    'product_type': t,
                    'allocation_percentage': int(100 / len(suggested_types)),
                    'reason': '基于风险等级的默认推荐（AI服务不可用）',
                    'suggested_products': [],
                    'risk_warnings': ['投资有风险，入市需谨慎']
                }
                for t in suggested_types
            ],
            'portfolio_summary': 'AI服务暂时不可用，无法生成详细配置建议',
            'expected_return_range': '无法预估',
            'risk_level': risk_level,
            'disclaimer': '投资有风险，入市需谨慎。AI服务暂时不可用，建议咨询专业投资顾问。',
            'ai_generated': False,
            'source': 'fallback'
        }
