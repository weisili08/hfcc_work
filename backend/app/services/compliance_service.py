"""
合规检查服务模块
提供AI合规检查和风险提示功能
"""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class ComplianceService:
    """
    合规检查服务类
    
    提供以下功能：
    - AI合规检查（内容、流程、交易、沟通）
    - 获取合规风险提示
    - 反洗钱初步检查
    """
    
    # 合规风险规则库
    RISK_RULES = [
        {
            'rule_id': 'COMP-001',
            'name': '虚假宣传',
            'keywords': ['保本', '保收益', '稳赚', '零风险', '绝对收益', '肯定赚钱'],
            'risk_level': 'critical',
            'description': '不得承诺保本保收益'
        },
        {
            'rule_id': 'COMP-002',
            'name': '收益承诺',
            'keywords': ['预期收益', '收益率', '年化收益', '回报'],
            'risk_level': 'high',
            'description': '不得对收益进行暗示或承诺'
        },
        {
            'rule_id': 'COMP-003',
            'name': '风险提示缺失',
            'keywords': [],
            'risk_level': 'high',
            'description': '必须包含投资风险提示'
        },
        {
            'rule_id': 'COMP-004',
            'name': '敏感词',
            'keywords': ['内幕', '消息股', '坐庄', '操纵市场'],
            'risk_level': 'critical',
            'description': '不得使用违规敏感词汇'
        },
        {
            'rule_id': 'COMP-005',
            'name': '适当性义务',
            'keywords': ['适合所有投资者', '人人可买', '无门槛'],
            'risk_level': 'medium',
            'description': '必须履行投资者适当性义务'
        }
    ]
    
    # 合规风险提示库
    RISK_TIPS = [
        {
            'tip_id': 'TIP-001',
            'scenario': '产品销售',
            'risk_type': '适当性义务',
            'risk_description': '未充分了解客户风险承受能力即推荐产品',
            'regulatory_requirement': '《证券期货投资者适当性管理办法》',
            'suggested_script': '根据您的风险测评结果，这款产品风险等级为R3，适合您当前的风险承受能力。请问您是否了解该产品的风险特征？',
            'severity': 'high'
        },
        {
            'tip_id': 'TIP-002',
            'scenario': '收益说明',
            'risk_type': '收益承诺',
            'risk_description': '暗示或承诺产品收益',
            'regulatory_requirement': '《基金募集机构投资者适当性管理实施指引》',
            'suggested_script': '基金过往业绩不代表未来表现，投资需谨慎。该产品历史业绩仅供参考，不构成收益承诺。',
            'severity': 'critical'
        },
        {
            'tip_id': 'TIP-003',
            'scenario': '风险提示',
            'risk_type': '风险提示缺失',
            'risk_description': '未充分揭示投资风险',
            'regulatory_requirement': '《公开募集证券投资基金销售机构监督管理办法》',
            'suggested_script': '在购买前，请您务必仔细阅读产品说明书和风险揭示书，充分了解产品风险。',
            'severity': 'high'
        },
        {
            'tip_id': 'TIP-004',
            'scenario': '客户沟通',
            'risk_type': '信息保密',
            'risk_description': '泄露客户信息或交易细节',
            'regulatory_requirement': '《证券投资基金法》',
            'suggested_script': '您的个人信息和交易记录我们会严格保密，请放心。',
            'severity': 'medium'
        },
        {
            'tip_id': 'TIP-005',
            'scenario': '投诉处理',
            'risk_type': '处理时效',
            'risk_description': '投诉处理超时',
            'regulatory_requirement': '《证券基金经营机构投诉处理工作管理办法》',
            'suggested_script': '您的投诉我们已记录，将在规定时限内给您回复，请保持联系方式畅通。',
            'severity': 'medium'
        }
    ]
    
    def __init__(self, llm_service, compliance_storage):
        """
        初始化合规检查服务
        
        Args:
            llm_service: LLM服务实例
            compliance_storage: 合规检查存储实例
        """
        self.llm_service = llm_service
        self.storage = compliance_storage
    
    def check_content(self, content: str, check_type: str = 'content') -> dict:
        """
        AI合规检查
        
        检查维度：虚假宣传、收益承诺、风险提示缺失、敏感词等
        
        Args:
            content: 待检查内容
            check_type: 检查类型 (content/process/transaction/communication)
            
        Returns:
            dict: 检查结果
        """
        # 基于规则的初步检查
        rule_findings = self._check_by_rules(content)
        
        # AI深度检查
        ai_findings = self._ai_compliance_check(content, check_type)
        
        # 合并检查结果
        all_findings = rule_findings + ai_findings.get('findings', [])
        
        # 确定整体结果和风险等级
        result = 'pass'
        risk_level = 'low'
        
        for finding in all_findings:
            if finding.get('risk_level') == 'critical':
                result = 'violation'
                risk_level = 'critical'
                break
            elif finding.get('risk_level') == 'high':
                result = 'warning'
                risk_level = 'high'
            elif finding.get('risk_level') == 'medium' and result == 'pass':
                result = 'warning'
                risk_level = 'medium'
        
        # 生成改进建议
        suggestions = self._generate_suggestions(all_findings)
        
        check_result = {
            'check_type': check_type,
            'result': result,
            'risk_level': risk_level,
            'findings': all_findings,
            'suggestions': suggestions,
            'content_preview': content[:200] + '...' if len(content) > 200 else content
        }
        
        # 保存检查记录
        try:
            self.storage.create_check({
                'check_type': check_type,
                'target_description': f'内容检查：{content[:50]}...',
                'content_to_check': content,
                'result': result,
                'risk_level': risk_level,
                'findings': all_findings,
                'suggestions': suggestions,
                'checked_by': 'ai_system'
            })
        except Exception as e:
            logger.error(f"Failed to save compliance check: {str(e)}")
        
        return check_result
    
    def get_risk_tips(self, scenario: str = None, risk_type: str = None) -> list:
        """
        获取合规风险提示
        
        Args:
            scenario: 场景筛选
            risk_type: 风险类型筛选
            
        Returns:
            list: 风险提示列表
        """
        tips = self.RISK_TIPS.copy()
        
        if scenario:
            tips = [t for t in tips if t['scenario'] == scenario]
        
        if risk_type:
            tips = [t for t in tips if t['risk_type'] == risk_type]
        
        return tips
    
    def check_aml(self, transaction_data: dict) -> dict:
        """
        反洗钱初步检查
        
        Args:
            transaction_data: 交易数据
            {
                'customer_id': '客户ID',
                'transaction_amount': 交易金额,
                'transaction_type': '交易类型',
                'counterparty': '交易对手',
                'frequency': '交易频率'
            }
            
        Returns:
            dict: 检查结果
        """
        risk_indicators = []
        overall_risk = 'low'
        
        # 检查大额交易
        amount = transaction_data.get('transaction_amount', 0)
        if amount >= 500000:  # 50万以上
            risk_indicators.append({
                'indicator_code': 'AML-001',
                'indicator_name': '大额交易',
                'risk_level': 'high',
                'description': f'交易金额{amount}元，超过大额交易标准',
                'triggered_rules': ['大额交易报告']
            })
            overall_risk = 'high'
        elif amount >= 200000:  # 20万以上
            risk_indicators.append({
                'indicator_code': 'AML-002',
                'indicator_name': '较大额交易',
                'risk_level': 'medium',
                'description': f'交易金额{amount}元，需关注',
                'triggered_rules': ['可疑交易监测']
            })
            if overall_risk == 'low':
                overall_risk = 'medium'
        
        # 检查交易频率
        frequency = transaction_data.get('frequency', '')
        if frequency in ['高频', '异常频繁']:
            risk_indicators.append({
                'indicator_code': 'AML-003',
                'indicator_name': '异常交易频率',
                'risk_level': 'high',
                'description': '交易频率异常，可能存在洗钱风险',
                'triggered_rules': ['可疑交易监测']
            })
            overall_risk = 'high'
        
        # 检查交易对手
        counterparty = transaction_data.get('counterparty', '')
        high_risk_regions = ['高风险地区A', '高风险地区B']
        if any(region in counterparty for region in high_risk_regions):
            risk_indicators.append({
                'indicator_code': 'AML-004',
                'indicator_name': '高风险地区交易',
                'risk_level': 'critical',
                'description': '交易涉及高风险地区',
                'triggered_rules': ['高风险地区监测']
            })
            overall_risk = 'critical'
        
        recommendations = []
        if overall_risk == 'critical':
            recommendations.append('立即上报可疑交易报告')
            recommendations.append('暂停相关交易')
            recommendations.append('加强客户尽职调查')
        elif overall_risk == 'high':
            recommendations.append('加强交易监测')
            recommendations.append('关注客户后续交易行为')
            recommendations.append('必要时进行客户回访')
        elif overall_risk == 'medium':
            recommendations.append('纳入关注名单')
            recommendations.append('定期复核交易情况')
        
        return {
            'check_type': 'aml',
            'status': 'completed',
            'risk_indicators': risk_indicators,
            'overall_risk_level': overall_risk,
            'recommendations': recommendations,
            'checked_at': self._get_timestamp()
        }
    
    def get_statistics(self) -> dict:
        """
        获取合规检查统计
        
        Returns:
            dict: 统计数据
        """
        return self.storage.get_statistics()
    
    def _check_by_rules(self, content: str) -> list:
        """
        基于规则检查内容
        
        Args:
            content: 待检查内容
            
        Returns:
            list: 发现的问题
        """
        findings = []
        content_lower = content.lower()
        
        for rule in self.RISK_RULES:
            for keyword in rule['keywords']:
                if keyword in content_lower:
                    findings.append({
                        'rule_id': rule['rule_id'],
                        'type': rule['name'],
                        'risk_level': rule['risk_level'],
                        'description': f"检测到违规关键词：'{keyword}' - {rule['description']}",
                        'keyword': keyword
                    })
                    break
        
        # 检查风险提示
        risk_keywords = ['风险', '投资需谨慎', '过往业绩不代表未来表现']
        has_risk_warning = any(kw in content for kw in risk_keywords)
        if not has_risk_warning:
            findings.append({
                'rule_id': 'COMP-003',
                'type': '风险提示缺失',
                'risk_level': 'high',
                'description': '内容中未检测到风险提示语句'
            })
        
        return findings
    
    def _ai_compliance_check(self, content: str, check_type: str) -> dict:
        """
        AI深度合规检查
        
        Args:
            content: 待检查内容
            check_type: 检查类型
            
        Returns:
            dict: AI检查结果
        """
        system_prompt = """你是一位资深的基金合规审查专家。
请对提供的内容进行合规性审查，识别潜在的合规风险。
重点关注：虚假宣传、收益承诺、风险提示、敏感词等。"""
        
        prompt = f"""请对以下内容进行合规检查：

检查类型：{check_type}
内容：
{content}

请按以下JSON格式返回检查结果：
{{
    "findings": [
        {{
            "type": "问题类型",
            "risk_level": "low/medium/high/critical",
            "description": "问题描述",
            "suggestion": "改进建议"
        }}
    ],
    "overall_assessment": "整体评估"
}}"""
        
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        if not result.get('success'):
            logger.warning(f"AI compliance check failed: {result.get('error')}")
            return {'findings': []}
        
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
            
            check_result = json.loads(json_str)
            return check_result
        except Exception as e:
            logger.error(f"Failed to parse AI check result: {str(e)}")
            return {'findings': []}
    
    def _generate_suggestions(self, findings: list) -> list:
        """
        生成改进建议
        
        Args:
            findings: 发现的问题列表
            
        Returns:
            list: 建议列表
        """
        suggestions = []
        
        for finding in findings:
            if finding.get('type') == '虚假宣传':
                suggestions.append('删除所有保本保收益的承诺性表述')
                suggestions.append('使用"业绩比较基准"替代"预期收益"')
            elif finding.get('type') == '收益承诺':
                suggestions.append('避免使用具体的收益数字或承诺')
                suggestions.append('强调"过往业绩不代表未来表现"')
            elif finding.get('type') == '风险提示缺失':
                suggestions.append('在显著位置添加风险提示语句')
                suggestions.append('确保风险等级与客户适当性匹配')
            elif finding.get('type') == '敏感词':
                suggestions.append('删除违规敏感词汇')
                suggestions.append('使用合规的专业术语替代')
        
        # 去重
        return list(set(suggestions)) if suggestions else ['内容合规，无需修改']
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
