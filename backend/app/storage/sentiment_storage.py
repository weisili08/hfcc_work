"""
舆情监测存储模块
提供舆情记录的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class SentimentRecordStorage(BaseStorage):
    """
    舆情记录存储类
    
    存储字段：
    - id: 记录ID (sen_{uuid})
    - title: 标题
    - source: 来源 (news/social_media/forum/official)
    - content: 内容
    - sentiment: 情感 (positive/neutral/negative)
    - severity: 严重程度 (critical/high/medium/low)
    - keywords: 关键词列表
    - related_products: 相关产品列表
    - status: 状态 (new/monitoring/resolved/archived)
    - alert_level: 预警级别
    - analysis: AI分析结果
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化舆情记录存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'sentiment_records.json')
    
    def create_record(self, record_data: dict) -> dict:
        """
        创建舆情记录
        
        Args:
            record_data: 记录数据字典
            
        Returns:
            dict: 创建后的完整记录
        """
        # 设置默认值
        if 'sentiment' not in record_data:
            record_data['sentiment'] = 'neutral'
        if 'severity' not in record_data:
            record_data['severity'] = 'low'
        if 'status' not in record_data:
            record_data['status'] = 'new'
        if 'keywords' not in record_data:
            record_data['keywords'] = []
        if 'related_products' not in record_data:
            record_data['related_products'] = []
        
        return self.create(record_data)
    
    def get_record_by_id(self, record_id: str) -> dict:
        """
        按ID获取舆情记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            dict: 记录，不存在返回None
        """
        return self.get(record_id)
    
    def update_record(self, record_id: str, updates: dict) -> dict:
        """
        更新舆情记录
        
        Args:
            record_id: 记录ID
            updates: 更新的字段
            
        Returns:
            dict: 更新后的记录
        """
        return self.update(record_id, updates)
    
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
        return self.list(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def get_records_by_sentiment(self, sentiment: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按情感倾向获取记录
        
        Args:
            sentiment: 情感倾向
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'sentiment': sentiment},
            page=page,
            page_size=page_size
        )
    
    def get_records_by_severity(self, severity: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按严重程度获取记录
        
        Args:
            severity: 严重程度
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'severity': severity},
            page=page,
            page_size=page_size
        )
    
    def get_records_by_status(self, status: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按状态获取记录
        
        Args:
            status: 状态
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'status': status},
            page=page,
            page_size=page_size
        )
    
    def get_alert_records(self, page: int = 1, page_size: int = 20) -> dict:
        """
        获取预警记录（高严重程度）
        
        Args:
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        data = self._load()
        
        # 过滤已删除和高严重程度记录
        items = [
            item for item in data 
            if item.get('deleted_at') is None 
            and item.get('severity') in ['critical', 'high']
        ]
        
        # 排序
        items = sorted(items, key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 分页
        total = len(items)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            'items': [item.copy() for item in items[start:end]],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }
    
    def get_dashboard_data(self) -> dict:
        """
        获取舆情监控面板数据
        
        Returns:
            dict: 面板数据
        """
        data = self._load()
        
        # 过滤已删除记录
        data = [item for item in data if item.get('deleted_at') is None]
        
        total = len(data)
        
        # 情感分布
        sentiment_dist = {'positive': 0, 'neutral': 0, 'negative': 0}
        for item in data:
            sentiment = item.get('sentiment', 'neutral')
            if sentiment in sentiment_dist:
                sentiment_dist[sentiment] += 1
        
        # 严重程度分布
        severity_dist = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for item in data:
            severity = item.get('severity', 'low')
            if severity in severity_dist:
                severity_dist[severity] += 1
        
        # 来源分布
        source_dist = {}
        for item in data:
            source = item.get('source', 'unknown')
            source_dist[source] = source_dist.get(source, 0) + 1
        
        # 预警数量
        alert_count = severity_dist['critical'] + severity_dist['high']
        
        # 最新记录
        latest = sorted(data, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        
        return {
            'total_records': total,
            'alert_count': alert_count,
            'sentiment_distribution': sentiment_dist,
            'severity_distribution': severity_dist,
            'source_distribution': source_dist,
            'latest_records': [item.copy() for item in latest]
        }
    
    def search_by_keywords(self, keywords: list) -> list:
        """
        按关键词搜索记录
        
        Args:
            keywords: 关键词列表
            
        Returns:
            list: 匹配的记录列表
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            item_keywords = item.get('keywords', [])
            # 检查是否有交集
            if any(kw in item_keywords for kw in keywords):
                results.append(item.copy())
        
        return results
