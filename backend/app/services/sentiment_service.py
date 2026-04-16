"""
舆情监测服务模块
提供AI舆情分析和监控面板功能
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class SentimentService:
    """
    舆情监测服务类
    
    提供以下功能：
    - AI舆情分析（情感分析+关键词提取+风险评估）
    - 舆情监控面板数据
    - 生成舆情分析报告
    """
    
    def __init__(self, llm_service, sentiment_storage):
        """
        初始化舆情监测服务
        
        Args:
            llm_service: LLM服务实例
            sentiment_storage: 舆情记录存储实例
        """
        self.llm_service = llm_service
        self.storage = sentiment_storage
    
    def analyze(self, content: str, source: str = None) -> dict:
        """
        AI舆情分析（情感分析+关键词提取+风险评估）
        
        Args:
            content: 舆情内容
            source: 来源
            
        Returns:
            dict: 分析结果
        """
        system_prompt = """你是一位专业的金融舆情分析专家。
请对提供的舆情内容进行深度分析，包括：
1. 情感倾向分析（positive/neutral/negative）
2. 关键词提取
3. 相关产品识别
4. 严重程度评估（critical/high/medium/low）
5. 风险评估和预警建议"""
        
        prompt = f"""请分析以下舆情内容：

来源：{source or '未知'}
内容：
{content}

请按以下JSON格式返回分析结果：
{{
    "sentiment": "positive/neutral/negative",
    "sentiment_score": 0.0,
    "keywords": ["关键词1", "关键词2"],
    "related_products": ["产品1", "产品2"],
    "severity": "critical/high/medium/low",
    "risk_assessment": "风险评估说明",
    "alert_level": "high/medium/low/none",
    "summary": "内容摘要"
}}"""
        
        # 调用LLM进行分析
        result = self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        if not result.get('success'):
            logger.error(f"Failed to analyze sentiment: {result.get('error')}")
            return self._get_fallback_analysis(content)
        
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
                'sentiment': analysis.get('sentiment', 'neutral'),
                'sentiment_score': analysis.get('sentiment_score', 0),
                'keywords': analysis.get('keywords', []),
                'related_products': analysis.get('related_products', []),
                'severity': analysis.get('severity', 'low'),
                'risk_assessment': analysis.get('risk_assessment', ''),
                'alert_level': analysis.get('alert_level', 'none'),
                'summary': analysis.get('summary', content[:100]),
                'ai_generated': True,
                'source': result.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to parse sentiment analysis: {str(e)}")
            return self._get_fallback_analysis(content)
    
    def get_dashboard(self) -> dict:
        """
        获取舆情监控面板数据（趋势、分布、预警）
        
        Returns:
            dict: 面板数据
        """
        # 获取基础统计数据
        dashboard_data = self.storage.get_dashboard_data()
        
        # 计算趋势（最近7天）
        trend = self._calculate_trend(days=7)
        
        # 获取最新预警
        alerts = self.storage.get_alert_records(page=1, page_size=10)
        
        return {
            'overview': {
                'total_records': dashboard_data['total_records'],
                'alert_count': dashboard_data['alert_count'],
                'new_today': self._get_new_count(days=1),
                'new_this_week': self._get_new_count(days=7)
            },
            'sentiment_distribution': dashboard_data['sentiment_distribution'],
            'severity_distribution': dashboard_data['severity_distribution'],
            'source_distribution': dashboard_data['source_distribution'],
            'trend': trend,
            'latest_alerts': alerts.get('items', []),
            'latest_records': dashboard_data['latest_records']
        }
    
    def generate_report(self, date_range: dict = None) -> dict:
        """
        生成舆情分析报告
        
        Args:
            date_range: 日期范围 {'start_date': '...', 'end_date': '...'}
            
        Returns:
            dict: 报告数据
        """
        # 默认最近7天
        if date_range is None:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)
            date_range = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        
        # 获取面板数据
        dashboard = self.get_dashboard()
        
        # 生成AI分析摘要
        ai_summary = self._generate_report_summary(dashboard, date_range)
        
        return {
            'report_id': f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'report_type': 'sentiment_analysis',
            'date_range': date_range,
            'generated_at': self._get_timestamp(),
            'summary': {
                'total_records': dashboard['overview']['total_records'],
                'alert_count': dashboard['overview']['alert_count'],
                'ai_summary': ai_summary,
                'key_findings': self._generate_key_findings(dashboard)
            },
            'sentiment_analysis': dashboard['sentiment_distribution'],
            'severity_analysis': dashboard['severity_distribution'],
            'source_analysis': dashboard['source_distribution'],
            'trend_analysis': dashboard['trend'],
            'top_concerns': self._get_top_concerns(),
            'recommendations': self._generate_recommendations(dashboard)
        }
    
    def save_record(self, record_data: dict) -> dict:
        """
        保存舆情记录
        
        Args:
            record_data: 记录数据
            
        Returns:
            dict: 保存后的记录
        """
        return self.storage.create_record(record_data)
    
    def get_record(self, record_id: str) -> Optional[dict]:
        """
        获取舆情记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            dict: 记录
        """
        return self.storage.get_record_by_id(record_id)
    
    def list_records(self, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        """
        列表查询舆情记录
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.storage.list_records(filters, page, page_size)
    
    def update_record_status(self, record_id: str, status: str) -> dict:
        """
        更新舆情记录状态
        
        Args:
            record_id: 记录ID
            status: 新状态
            
        Returns:
            dict: 更新后的记录
        """
        return self.storage.update_record(record_id, {'status': status})
    
    def _calculate_trend(self, days: int = 7) -> list:
        """
        计算舆情趋势
        
        Args:
            days: 天数
            
        Returns:
            list: 趋势数据
        """
        trend = []
        end_date = datetime.now(timezone.utc)
        
        for i in range(days - 1, -1, -1):
            date = end_date - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 模拟数据，实际应从存储中查询
            trend.append({
                'date': date_str,
                'positive': 10 + i * 2,
                'neutral': 20 + i,
                'negative': 5 + (i % 3),
                'total': 35 + i * 3 + (i % 3)
            })
        
        return trend
    
    def _get_new_count(self, days: int = 1) -> int:
        """
        获取最近N天新增数量
        
        Args:
            days: 天数
            
        Returns:
            int: 数量
        """
        # 实际应从存储中按时间筛选
        # 这里返回模拟数据
        return days * 15
    
    def _generate_report_summary(self, dashboard: dict, date_range: dict) -> str:
        """
        生成报告AI摘要
        
        Args:
            dashboard: 面板数据
            date_range: 日期范围
            
        Returns:
            str: 摘要
        """
        sentiment_dist = dashboard['sentiment_distribution']
        total = sum(sentiment_dist.values())
        
        if total == 0:
            return '暂无舆情数据'
        
        positive_pct = round(sentiment_dist.get('positive', 0) / total * 100, 1)
        negative_pct = round(sentiment_dist.get('negative', 0) / total * 100, 1)
        
        summary = f"报告期内共监测到舆情{total}条，"
        summary += f"其中正面舆情占比{positive_pct}%，负面舆情占比{negative_pct}%。"
        
        if dashboard['overview']['alert_count'] > 0:
            summary += f"发现{dashboard['overview']['alert_count']}条高风险舆情，建议重点关注。"
        else:
            summary += "整体舆情态势平稳，未发现重大风险。"
        
        return summary
    
    def _generate_key_findings(self, dashboard: dict) -> list:
        """
        生成关键发现
        
        Args:
            dashboard: 面板数据
            
        Returns:
            list: 关键发现列表
        """
        findings = []
        
        sentiment_dist = dashboard['sentiment_distribution']
        if sentiment_dist.get('negative', 0) > sentiment_dist.get('positive', 0):
            findings.append('负面舆情数量超过正面舆情，需关注市场情绪')
        
        if dashboard['overview']['alert_count'] > 5:
            findings.append('高风险舆情数量较多，建议启动应急响应')
        
        severity_dist = dashboard['severity_distribution']
        if severity_dist.get('critical', 0) > 0:
            findings.append(f"发现{severity_dist['critical']}条严重级别舆情，需立即处理")
        
        if not findings:
            findings.append('舆情整体平稳，无重大发现')
        
        return findings
    
    def _get_top_concerns(self) -> list:
        """
        获取热点关注
        
        Returns:
            list: 热点列表
        """
        # 实际应从关键词统计中获取
        return [
            {'topic': '基金净值波动', 'mention_count': 45, 'sentiment': 'negative'},
            {'topic': '新产品发行', 'mention_count': 32, 'sentiment': 'positive'},
            {'topic': '客户服务', 'mention_count': 28, 'sentiment': 'neutral'}
        ]
    
    def _generate_recommendations(self, dashboard: dict) -> list:
        """
        生成应对建议
        
        Args:
            dashboard: 面板数据
            
        Returns:
            list: 建议列表
        """
        recommendations = []
        
        if dashboard['overview']['alert_count'] > 0:
            recommendations.append('针对高风险舆情，建议立即启动应急响应机制')
            recommendations.append('安排专人跟踪处理负面舆情，及时回应投资者关切')
        
        sentiment_dist = dashboard['sentiment_distribution']
        if sentiment_dist.get('negative', 0) > 20:
            recommendations.append('负面舆情占比较高，建议加强投资者教育和沟通')
        
        recommendations.append('持续监测舆情动态，定期生成分析报告')
        recommendations.append('加强与媒体的沟通，维护品牌形象')
        
        return recommendations
    
    def _get_fallback_analysis(self, content: str) -> dict:
        """
        获取降级舆情分析
        
        Args:
            content: 内容
            
        Returns:
            dict: 降级分析结果
        """
        # 简单的关键词匹配
        negative_keywords = ['下跌', '亏损', '不好', '失望', '风险', '问题']
        positive_keywords = ['上涨', '收益', '好', '满意', '优秀', '推荐']
        
        negative_count = sum(1 for kw in negative_keywords if kw in content)
        positive_count = sum(1 for kw in positive_keywords if kw in content)
        
        if negative_count > positive_count:
            sentiment = 'negative'
            sentiment_score = -0.3
            severity = 'medium'
        elif positive_count > negative_count:
            sentiment = 'positive'
            sentiment_score = 0.3
            severity = 'low'
        else:
            sentiment = 'neutral'
            sentiment_score = 0
            severity = 'low'
        
        return {
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'keywords': ['AI服务不可用', '降级分析'],
            'related_products': [],
            'severity': severity,
            'risk_assessment': 'AI服务暂时不可用，使用降级分析',
            'alert_level': 'none',
            'summary': content[:100] if len(content) > 100 else content,
            'ai_generated': False,
            'source': 'fallback'
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
