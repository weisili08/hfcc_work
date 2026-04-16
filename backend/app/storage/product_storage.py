"""
产品分析存储模块
提供产品分析的CRUD操作
"""

from app.storage.base_storage import BaseStorage


class ProductAnalysisStorage(BaseStorage):
    """
    产品分析存储类
    
    存储字段：
    - id: 分析ID (prod_{uuid})
    - product_name: 产品名称
    - product_type: 产品类型 (equity_fund/bond_fund/money_market/mixed/index)
    - company: 基金公司
    - analysis_content: 分析内容
    - performance_data: 业绩数据
    - risk_metrics: 风险指标
    - comparison_products: 对比产品列表
    - recommendation: 推荐建议
    - status: 状态 (draft/published)
    - created_by: 创建人
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        """
        初始化产品分析存储
        
        Args:
            data_dir: 数据目录路径
        """
        super().__init__(data_dir, 'product_analyses.json')
    
    def create_analysis(self, analysis_data: dict) -> dict:
        """
        创建产品分析
        
        Args:
            analysis_data: 分析数据字典
            
        Returns:
            dict: 创建后的完整记录
        """
        # 设置默认值
        if 'status' not in analysis_data:
            analysis_data['status'] = 'draft'
        if 'performance_data' not in analysis_data:
            analysis_data['performance_data'] = {}
        if 'risk_metrics' not in analysis_data:
            analysis_data['risk_metrics'] = {}
        if 'comparison_products' not in analysis_data:
            analysis_data['comparison_products'] = []
        
        return self.create(analysis_data)
    
    def get_analysis_by_id(self, analysis_id: str) -> dict:
        """
        按ID获取产品分析
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            dict: 分析记录，不存在返回None
        """
        return self.get(analysis_id)
    
    def get_analysis_by_product_name(self, product_name: str) -> dict:
        """
        按产品名称获取分析
        
        Args:
            product_name: 产品名称
            
        Returns:
            dict: 分析记录，不存在返回None
        """
        data = self._load()
        for item in data:
            if item.get('deleted_at') is None and item.get('product_name') == product_name:
                return item.copy()
        return None
    
    def update_analysis(self, analysis_id: str, updates: dict) -> dict:
        """
        更新产品分析
        
        Args:
            analysis_id: 分析ID
            updates: 更新的字段
            
        Returns:
            dict: 更新后的记录
        """
        return self.update(analysis_id, updates)
    
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
        return self.list(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def get_analyses_by_type(self, product_type: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按产品类型获取分析
        
        Args:
            product_type: 产品类型
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'product_type': product_type},
            page=page,
            page_size=page_size
        )
    
    def get_analyses_by_company(self, company: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按基金公司获取分析
        
        Args:
            company: 基金公司
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'company': company},
            page=page,
            page_size=page_size
        )
    
    def get_published_analyses(self, page: int = 1, page_size: int = 20) -> dict:
        """
        获取已发布的分析
        
        Args:
            page: 页码
            page_size: 每页条数
            
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'status': 'published'},
            page=page,
            page_size=page_size
        )
    
    def search_analyses(self, keyword: str) -> list:
        """
        搜索产品分析
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的分析列表
        """
        return self.search(keyword, fields=['product_name', 'company', 'analysis_content'])
