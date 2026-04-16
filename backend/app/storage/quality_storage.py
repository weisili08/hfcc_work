"""
质检管理存储模块
提供质检记录的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class QualityCheckStorage(BaseStorage):
    """
    质检记录存储类
    
    字段：
    - id: 唯一标识
    - agent_name: 客服姓名
    - call_date: 通话日期
    - call_duration: 通话时长（秒）
    - call_content: 通话内容
    - status: 状态 (pending/analyzing/completed)
    - overall_score: 综合评分
    - scores: 分项评分 {attitude, professionalism, compliance, problem_solving}
    - issues: 问题点列表
    - suggestions: 改进建议列表
    - analyzed_by: 分析来源（AI/人工）
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化质检存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'quality_checks.json')
    
    def get_by_status(self, status: str) -> list:
        """
        按状态查询质检记录
        
        Args:
            status: 状态
        
        Returns:
            list: 符合条件的记录列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('status') == status and item.get('deleted_at') is None
        ]
    
    def get_by_agent(self, agent_name: str) -> list:
        """
        按客服姓名查询质检记录
        
        Args:
            agent_name: 客服姓名
        
        Returns:
            list: 符合条件的记录列表
        """
        data = self._load()
        return [
            item.copy() for item in data 
            if item.get('agent_name') == agent_name and item.get('deleted_at') is None
        ]
    
    def update_analysis_result(self, check_id: str, result: dict) -> dict:
        """
        更新质检分析结果
        
        Args:
            check_id: 质检记录ID
            result: 分析结果
                - overall_score: 综合评分
                - scores: 分项评分
                - issues: 问题点
                - suggestions: 建议
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {
            'status': 'completed',
            'overall_score': result.get('overall_score'),
            'scores': result.get('scores', {}),
            'issues': result.get('issues', []),
            'suggestions': result.get('suggestions', []),
            'analyzed_by': result.get('analyzed_by', 'AI')
        }
        
        return self.update(check_id, updates)
    
    def update_status(self, check_id: str, status: str) -> dict:
        """
        更新质检状态
        
        Args:
            check_id: 质检记录ID
            status: 新状态
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(check_id, {'status': status})
    
    def get_statistics(self, date_range: dict = None) -> dict:
        """
        获取质检统计数据
        
        Args:
            date_range: 日期范围 {'start': '2026-01-01', 'end': '2026-12-31'}
        
        Returns:
            dict: 统计数据
        """
        data = self._load()
        records = [item for item in data if item.get('deleted_at') is None]
        
        # 按日期范围过滤
        if date_range:
            start_date = date_range.get('start')
            end_date = date_range.get('end')
            if start_date or end_date:
                filtered = []
                for item in records:
                    call_date = item.get('call_date', '')
                    if start_date and call_date < start_date:
                        continue
                    if end_date and call_date > end_date:
                        continue
                    filtered.append(item)
                records = filtered
        
        total = len(records)
        completed_records = [item for item in records if item.get('status') == 'completed']
        
        # 平均分统计
        avg_overall = 0
        avg_attitude = 0
        avg_professionalism = 0
        avg_compliance = 0
        avg_problem_solving = 0
        
        if completed_records:
            avg_overall = sum(item.get('overall_score', 0) for item in completed_records) / len(completed_records)
            avg_attitude = sum(item.get('scores', {}).get('attitude', 0) for item in completed_records) / len(completed_records)
            avg_professionalism = sum(item.get('scores', {}).get('professionalism', 0) for item in completed_records) / len(completed_records)
            avg_compliance = sum(item.get('scores', {}).get('compliance', 0) for item in completed_records) / len(completed_records)
            avg_problem_solving = sum(item.get('scores', {}).get('problem_solving', 0) for item in completed_records) / len(completed_records)
        
        # 评分分布
        score_distribution = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        for item in completed_records:
            score = item.get('overall_score', 0)
            if score >= 90:
                score_distribution['excellent'] += 1
            elif score >= 80:
                score_distribution['good'] += 1
            elif score >= 60:
                score_distribution['average'] += 1
            else:
                score_distribution['poor'] += 1
        
        # 统计常见问题TOP5
        issue_counts = {}
        for item in completed_records:
            for issue in item.get('issues', []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 按状态统计
        status_counts = {}
        for item in records:
            status = item.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total': total,
            'completed_count': len(completed_records),
            'average_scores': {
                'overall': round(avg_overall, 2),
                'attitude': round(avg_attitude, 2),
                'professionalism': round(avg_professionalism, 2),
                'compliance': round(avg_compliance, 2),
                'problem_solving': round(avg_problem_solving, 2)
            },
            'score_distribution': score_distribution,
            'top_issues': [{'issue': issue, 'count': count} for issue, count in top_issues],
            'status_counts': status_counts
        }
    
    def get_agent_statistics(self, agent_name: str) -> dict:
        """
        获取指定客服的质检统计
        
        Args:
            agent_name: 客服姓名
        
        Returns:
            dict: 统计数据
        """
        records = self.get_by_agent(agent_name)
        completed_records = [item for item in records if item.get('status') == 'completed']
        
        if not completed_records:
            return {
                'agent_name': agent_name,
                'total_checks': 0,
                'average_score': 0,
                'latest_score': 0
            }
        
        avg_score = sum(item.get('overall_score', 0) for item in completed_records) / len(completed_records)
        latest = max(completed_records, key=lambda x: x.get('created_at', ''))
        
        return {
            'agent_name': agent_name,
            'total_checks': len(completed_records),
            'average_score': round(avg_score, 2),
            'latest_score': latest.get('overall_score', 0)
        }
