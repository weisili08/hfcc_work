"""
异常识别服务模块
提供AI驱动的异常交易检测和分析功能
"""

import json
import logging

logger = logging.getLogger(__name__)


class AnomalyService:
    """
    异常识别服务类
    
    提供异常交易检测、告警分析等功能
    """
    
    def __init__(self, llm_service, anomaly_storage):
        """
        初始化异常识别服务
        
        Args:
            llm_service: LLM服务实例
            anomaly_storage: 异常告警存储实例
        """
        self.llm_service = llm_service
        self.anomaly_storage = anomaly_storage
    
    def detect(self, transaction_data: dict) -> dict:
        """
        检测异常交易
        
        基于规则+AI分析检测交易中的异常情况
        
        Args:
            transaction_data: 交易数据，包含客户信息、交易明细等
        
        Returns:
            dict: 检测结果，包含是否异常、异常类型、严重程度等
        """
        try:
            # 首先进行规则检测
            rule_result = self._rule_based_detection(transaction_data)
            
            # 如果规则检测到明显异常，直接返回
            if rule_result.get('is_anomaly') and rule_result.get('severity') in ['critical', 'high']:
                return rule_result
            
            # 使用AI进行深度分析
            system_prompt = """你是一位专业的基金交易风控分析师，擅长识别交易中的异常模式。
请分析提供的交易数据，判断是否存在以下异常类型：
- large_redemption: 大额赎回
- frequent_complaint: 频繁投诉关联
- unusual_transaction: 异常交易模式
- dormant_account: 休眠账户激活

请以JSON格式返回分析结果：
{
    "is_anomaly": true/false,
    "alert_type": "异常类型",
    "severity": "critical/high/medium/low",
    "description": "异常描述",
    "reasoning": "分析理由"
}"""
            
            transaction_json = json.dumps(transaction_data, ensure_ascii=False, indent=2)
            prompt = f"请分析以下交易数据是否存在异常：\n\n{transaction_json}"
            
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            if not result.get('success'):
                logger.warning(f"LLM异常检测失败: {result.get('error')}")
                return rule_result
            
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
                
                # 合并规则和AI结果
                if ai_result.get('is_anomaly'):
                    return {
                        'is_anomaly': True,
                        'alert_type': ai_result.get('alert_type', rule_result.get('alert_type')),
                        'severity': ai_result.get('severity', rule_result.get('severity')),
                        'description': ai_result.get('description', rule_result.get('description')),
                        'reasoning': ai_result.get('reasoning', ''),
                        'source': 'ai_detection'
                    }
                
                return rule_result
                
            except json.JSONDecodeError as e:
                logger.error(f"解析AI检测结果失败: {e}")
                return rule_result
                
        except Exception as e:
            logger.error(f"异常检测服务异常: {e}")
            return {'is_anomaly': False, 'error': str(e)}
    
    def analyze(self, alert_id: str) -> dict:
        """
        AI分析异常原因
        
        对已创建的告警进行深度分析，生成处理建议
        
        Args:
            alert_id: 告警ID
        
        Returns:
            dict: 分析结果
        """
        alert = self.anomaly_storage.get(alert_id)
        if not alert:
            return {'error': '告警不存在'}
        
        try:
            system_prompt = """你是一位资深的基金风控专家，擅长分析异常交易的原因和影响。
请基于告警信息，提供以下分析：
1. 异常原因分析
2. 潜在风险评估
3. 处理建议
4. 后续跟进措施

请以JSON格式返回分析结果。"""
            
            alert_json = json.dumps(alert, ensure_ascii=False, indent=2)
            prompt = f"请分析以下异常告警并提供处理建议：\n\n{alert_json}"
            
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=1000
            )
            
            if not result.get('success'):
                return self._get_fallback_analysis(alert)
            
            content = result.get('content', '')
            
            # 尝试解析JSON
            try:
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    analysis = json.loads(json_str)
                else:
                    analysis = {'detailed_analysis': content}
                
                # 更新告警记录
                analysis_text = analysis.get('detailed_analysis', '') or json.dumps(analysis, ensure_ascii=False)
                self.anomaly_storage.update_status(alert_id, alert.get('status'), analysis_text)
                
                analysis['alert_id'] = alert_id
                return analysis
                
            except json.JSONDecodeError:
                # 更新告警记录
                self.anomaly_storage.update_status(alert_id, alert.get('status'), content)
                return {
                    'alert_id': alert_id,
                    'analysis': content,
                    'source': 'ai_analysis'
                }
                
        except Exception as e:
            logger.error(f"异常分析服务异常: {e}")
            return self._get_fallback_analysis(alert)
    
    def create_alert(self, customer_id: str, customer_name: str, transaction_data: dict) -> dict:
        """
        创建异常告警
        
        检测交易并自动创建告警（如果检测到异常）
        
        Args:
            customer_id: 客户ID
            customer_name: 客户姓名
            transaction_data: 交易数据
        
        Returns:
            dict: 创建的告警或检测结果
        """
        detection_result = self.detect(transaction_data)
        
        if detection_result.get('is_anomaly'):
            alert = self.anomaly_storage.create_alert(
                customer_id=customer_id,
                customer_name=customer_name,
                alert_type=detection_result.get('alert_type', 'unusual_transaction'),
                severity=detection_result.get('severity', 'medium'),
                description=detection_result.get('description', '检测到异常交易')
            )
            
            alert['detection_source'] = detection_result.get('source', 'rule')
            return {'alert_created': True, 'alert': alert}
        
        return {'alert_created': False, 'detection_result': detection_result}
    
    def batch_detect(self, transactions: list) -> list:
        """
        批量检测异常
        
        Args:
            transactions: 交易数据列表
        
        Returns:
            list: 检测结果列表
        """
        results = []
        for transaction in transactions:
            result = self.detect(transaction)
            result['transaction_id'] = transaction.get('id')
            results.append(result)
        
        return results
    
    def _rule_based_detection(self, transaction_data: dict) -> dict:
        """
        基于规则的异常检测
        
        使用预定义规则快速检测明显异常
        """
        amount = transaction_data.get('amount', 0)
        transaction_type = transaction_data.get('type', '')
        customer_aum = transaction_data.get('customer_aum', 0)
        
        # 规则1: 大额赎回检测
        if transaction_type == 'redemption':
            if customer_aum > 0 and amount / customer_aum >= 0.5:
                return {
                    'is_anomaly': True,
                    'alert_type': 'large_redemption',
                    'severity': 'critical' if amount / customer_aum >= 0.8 else 'high',
                    'description': f'检测到大额赎回：赎回金额占资产比例{(amount/customer_aum)*100:.1f}%',
                    'source': 'rule_detection'
                }
            
            if amount >= 500000:
                return {
                    'is_anomaly': True,
                    'alert_type': 'large_redemption',
                    'severity': 'high',
                    'description': f'检测到单笔大额赎回：{amount}元',
                    'source': 'rule_detection'
                }
        
        # 规则2: 高频交易检测
        daily_count = transaction_data.get('daily_transaction_count', 0)
        if daily_count >= 5:
            return {
                'is_anomaly': True,
                'alert_type': 'unusual_transaction',
                'severity': 'medium',
                'description': f'检测到高频交易：单日交易{daily_count}笔',
                'source': 'rule_detection'
            }
        
        # 规则3: 休眠账户激活
        days_since_last = transaction_data.get('days_since_last_transaction', 0)
        if days_since_last >= 180:
            return {
                'is_anomaly': True,
                'alert_type': 'dormant_account',
                'severity': 'low',
                'description': f'休眠账户({days_since_last}天未交易)发生新交易',
                'source': 'rule_detection'
            }
        
        return {
            'is_anomaly': False,
            'source': 'rule_detection'
        }
    
    def _get_fallback_analysis(self, alert: dict) -> dict:
        """
        获取降级分析结果
        """
        alert_type = alert.get('alert_type', 'unusual_transaction')
        
        type_analysis = {
            'large_redemption': {
                'cause_analysis': '客户可能因资金需求、对产品收益不满或市场风险担忧而进行大额赎回。',
                'risk_assessment': '高。大额赎回可能影响客户资产配置，需及时了解赎回原因。',
                'handling_suggestions': [
                    '立即联系客户了解赎回原因',
                    '评估客户是否对产品或服务不满',
                    '提供替代投资建议'
                ],
                'follow_up': '持续跟进客户资金流向，争取资金回流。'
            },
            'frequent_complaint': {
                'cause_analysis': '客户可能对服务质量或产品表现存在持续不满。',
                'risk_assessment': '中高。频繁投诉可能导致客户流失和负面口碑传播。',
                'handling_suggestions': [
                    '升级投诉处理级别',
                    '安排专人跟进解决',
                    '评估是否需要服务补偿'
                ],
                'follow_up': '定期回访确认问题解决情况。'
            },
            'unusual_transaction': {
                'cause_analysis': '可能存在账户异常或客户交易行为突变。',
                'risk_assessment': '中。需要确认交易是否为客户本人操作。',
                'handling_suggestions': [
                    '核实交易真实性',
                    '确认客户账户安全',
                    '了解交易背景'
                ],
                'follow_up': '关注后续交易行为。'
            },
            'dormant_account': {
                'cause_analysis': '休眠账户重新激活，可能是客户重新关注投资。',
                'risk_assessment': '低。这是积极的信号，表明客户可能重新参与投资。',
                'handling_suggestions': [
                    '主动联系欢迎客户回归',
                    '了解客户当前投资需求',
                    '推荐适合的产品'
                ],
                'follow_up': '持续维护客户关系，避免再次休眠。'
            }
        }
        
        return type_analysis.get(alert_type, {
            'cause_analysis': '需要进一步调查异常原因。',
            'risk_assessment': '待评估',
            'handling_suggestions': ['及时跟进处理'],
            'follow_up': '持续监控'
        })
