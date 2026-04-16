"""
报表服务模块
提供AI驱动的报表生成和分析功能
"""

import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ReportService:
    """
    报表服务类
    
    提供报表生成、AI摘要生成、数据分析等功能
    """
    
    def __init__(self, llm_service, report_storage, 
                 profile_storage=None, anomaly_storage=None, churn_storage=None):
        """
        初始化报表服务
        
        Args:
            llm_service: LLM服务实例
            report_storage: 报表存储实例
            profile_storage: 客户画像存储实例（可选）
            anomaly_storage: 异常告警存储实例（可选）
            churn_storage: 流失风险存储实例（可选）
        """
        self.llm_service = llm_service
        self.report_storage = report_storage
        self.profile_storage = profile_storage
        self.anomaly_storage = anomaly_storage
        self.churn_storage = churn_storage
    
    def generate(self, report_type: str, parameters: dict, created_by: str = 'system') -> dict:
        """
        生成报表（含AI摘要和解读）
        
        Args:
            report_type: 报表类型 (daily/weekly/monthly/custom)
            parameters: 报表参数，包含时间范围、类别等
            created_by: 创建者
        
        Returns:
            dict: 生成的报表
        """
        category = parameters.get('category', 'service')
        
        # 创建报表记录
        title = self._generate_report_title(report_type, category, parameters)
        report = self.report_storage.create_report(
            title=title,
            report_type=report_type,
            category=category,
            parameters=parameters,
            created_by=created_by
        )
        
        # 更新状态为生成中
        self.report_storage.update_status(report['id'], 'generating')
        
        try:
            # 收集报表数据
            report_data = self._collect_report_data(category, parameters)
            
            # 生成AI摘要和解读
            ai_summary = self._generate_ai_summary(report_data, category)
            
            # 构建报表内容
            content = {
                'data': report_data,
                'generated_at': datetime.now().isoformat(),
                'parameters': parameters
            }
            
            # 更新报表
            self.report_storage.update_content(
                report_id=report['id'],
                content=content,
                summary=ai_summary.get('summary', '')
            )
            
            # 标记为完成
            updated_report = self.report_storage.update_status(report['id'], 'completed')
            updated_report['ai_summary'] = ai_summary
            
            return updated_report
            
        except Exception as e:
            logger.error(f"生成报表异常: {e}")
            self.report_storage.update_status(report['id'], 'failed')
            return {'error': f'报表生成失败: {str(e)}', 'report_id': report['id']}
    
    def get_summary(self, report_id: str) -> dict:
        """
        获取报表AI摘要
        
        Args:
            report_id: 报表ID
        
        Returns:
            dict: 报表摘要
        """
        report = self.report_storage.get(report_id)
        if not report:
            return {'error': '报表不存在'}
        
        return {
            'report_id': report_id,
            'title': report.get('title'),
            'summary': report.get('summary'),
            'category': report.get('category'),
            'type': report.get('type'),
            'created_at': report.get('created_at')
        }
    
    def generate_daily_report(self, date: str = None) -> dict:
        """
        生成日报
        
        Args:
            date: 日期字符串，默认昨天
        
        Returns:
            dict: 生成的日报
        """
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        parameters = {
            'date': date,
            'category': 'service',
            'start_date': date,
            'end_date': date
        }
        
        return self.generate('daily', parameters)
    
    def generate_weekly_report(self, week_start: str = None) -> dict:
        """
        生成周报
        
        Args:
            week_start: 周开始日期，默认上周一
        
        Returns:
            dict: 生成的周报
        """
        if not week_start:
            today = datetime.now()
            monday = today - timedelta(days=today.weekday() + 7)
            week_start = monday.strftime('%Y-%m-%d')
        
        week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        
        parameters = {
            'week_start': week_start,
            'week_end': week_end,
            'category': 'service',
            'start_date': week_start,
            'end_date': week_end
        }
        
        return self.generate('weekly', parameters)
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> dict:
        """
        生成月报
        
        Args:
            year: 年份，默认今年
            month: 月份，默认上月
        
        Returns:
            dict: 生成的月报
        """
        now = datetime.now()
        
        if year is None:
            year = now.year
        if month is None:
            month = now.month - 1
            if month == 0:
                month = 12
                year -= 1
        
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        parameters = {
            'year': year,
            'month': month,
            'category': 'service',
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self.generate('monthly', parameters)
    
    def _collect_report_data(self, category: str, parameters: dict) -> dict:
        """
        收集报表数据
        """
        data = {
            'category': category,
            'parameters': parameters,
            'collected_at': datetime.now().isoformat()
        }
        
        # 根据类别收集不同数据
        if category == 'customer' and self.profile_storage:
            # 客户分析数据
            stats = self.profile_storage.get_tag_statistics()
            data['customer_stats'] = stats
            
        elif category == 'complaint' and self.anomaly_storage:
            # 投诉相关数据
            stats = self.anomaly_storage.get_statistics()
            data['anomaly_stats'] = stats
            
        elif category == 'service':
            # 综合服务数据
            if self.profile_storage:
                data['customer_stats'] = self.profile_storage.get_tag_statistics()
            if self.anomaly_storage:
                data['anomaly_stats'] = self.anomaly_storage.get_statistics()
            if self.churn_storage:
                data['churn_stats'] = self.churn_storage.get_statistics()
        
        return data
    
    def _generate_ai_summary(self, report_data: dict, category: str) -> dict:
        """
        生成AI摘要
        """
        try:
            system_prompt = """你是一位专业的基金业务分析师，擅长生成数据报表的摘要和解读。
请基于提供的报表数据，生成以下内容：
1. 核心发现（3-5点）
2. 数据趋势分析
3. 风险提示（如有）
4. 改进建议
5. 一句话总结

请以JSON格式返回结果。"""
            
            data_json = json.dumps(report_data, ensure_ascii=False, indent=2, default=str)
            prompt = f"请为以下{category}类别的报表数据生成AI摘要和解读：\n\n{data_json}"
            
            result = self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=1500
            )
            
            if not result.get('success'):
                return self._get_fallback_summary(report_data, category)
            
            content = result.get('content', '')
            
            # 尝试解析JSON
            try:
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    summary = json.loads(json_str)
                else:
                    summary = {'summary': content}
                
                summary['source'] = 'ai_generation'
                return summary
                
            except json.JSONDecodeError:
                return {
                    'summary': content,
                    'source': 'ai_generation'
                }
                
        except Exception as e:
            logger.error(f"生成AI摘要异常: {e}")
            return self._get_fallback_summary(report_data, category)
    
    def _generate_report_title(self, report_type: str, category: str, parameters: dict) -> str:
        """
        生成报表标题
        """
        type_names = {
            'daily': '日报',
            'weekly': '周报',
            'monthly': '月报',
            'custom': '自定义报表'
        }
        
        category_names = {
            'service': '服务分析',
            'complaint': '投诉分析',
            'quality': '质量分析',
            'customer': '客户分析'
        }
        
        type_name = type_names.get(report_type, '报表')
        category_name = category_names.get(category, '综合')
        
        if report_type == 'daily':
            date = parameters.get('date', datetime.now().strftime('%Y-%m-%d'))
            return f"{category_name}{type_name} ({date})"
        elif report_type == 'weekly':
            week_start = parameters.get('week_start', '')
            return f"{category_name}{type_name} ({week_start}起)"
        elif report_type == 'monthly':
            year = parameters.get('year', datetime.now().year)
            month = parameters.get('month', datetime.now().month)
            return f"{category_name}{type_name} ({year}年{month}月)"
        else:
            return f"{category_name}{type_name}"
    
    def _get_fallback_summary(self, report_data: dict, category: str) -> dict:
        """
        获取降级摘要
        """
        category_summaries = {
            'customer': {
                'key_findings': [
                    '客户画像数据已收集完成',
                    '建议持续关注高价值客户维护',
                    '新客户获取渠道需要优化'
                ],
                'trend_analysis': '客户数据整体稳定，建议加强客户分层运营。',
                'risk_warnings': ['需关注客户流失风险'],
                'improvement_suggestions': ['完善客户标签体系', '提升客户服务质量'],
                'one_sentence_summary': '客户运营数据正常，建议持续优化客户体验。'
            },
            'complaint': {
                'key_findings': [
                    '投诉处理情况已汇总',
                    '建议加强投诉预警机制',
                    '提升首次解决率'
                ],
                'trend_analysis': '投诉处理效率有待提升。',
                'risk_warnings': ['投诉升级风险'],
                'improvement_suggestions': ['优化投诉处理流程', '加强员工培训'],
                'one_sentence_summary': '投诉管理需要持续改进，建议完善处理机制。'
            },
            'service': {
                'key_findings': [
                    '服务运营数据已汇总',
                    '客户满意度保持稳定',
                    '服务效率有提升空间'
                ],
                'trend_analysis': '服务运营整体平稳，各项指标在正常范围内。',
                'risk_warnings': ['需关注服务响应时间'],
                'improvement_suggestions': ['优化服务流程', '加强团队培训'],
                'one_sentence_summary': '服务运营情况良好，建议持续优化服务体验。'
            },
            'quality': {
                'key_findings': [
                    '质量监控数据已汇总',
                    '质检合格率达标',
                    '持续改进空间存在'
                ],
                'trend_analysis': '质量管理稳定，符合预期目标。',
                'risk_warnings': ['个别环节质量波动'],
                'improvement_suggestions': ['强化质量监控', '完善质检标准'],
                'one_sentence_summary': '质量管理情况良好，建议持续监控改进。'
            }
        }
        
        summary = category_summaries.get(category, category_summaries['service']).copy()
        summary['source'] = 'fallback'
        
        return summary
