"""
基础存储类模块
提供JSON文件存储的通用CRUD操作
支持线程安全、软删除、分页查询
"""

import os
import json
import uuid
import threading
from datetime import datetime, timezone
from typing import Optional


class BaseStorage:
    """
    JSON文件存储基类
    
    提供通用的CRUD操作，支持：
    - 线程安全（使用threading.Lock）
    - 软删除（deleted_at字段）
    - 分页查询
    - 关键词搜索
    - 自动时间戳管理
    """
    
    def __init__(self, data_dir: str, filename: str):
        """
        初始化存储实例
        
        Args:
            data_dir: 数据目录路径
            filename: JSON文件名（不含路径）
        """
        self.data_dir = data_dir
        self.filename = filename
        self.filepath = os.path.join(data_dir, filename)
        
        # 线程锁，保证文件操作线程安全
        self._lock = threading.Lock()
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
    
    def _load(self) -> list:
        """
        从JSON文件加载数据
        
        Returns:
            list: 数据列表，文件不存在时返回空列表
        """
        if not os.path.exists(self.filepath):
            return []
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 支持标准格式 {"metadata": {...}, "records": [...]}
                if isinstance(data, dict) and 'records' in data:
                    return data['records']
                # 也支持直接存储列表
                elif isinstance(data, list):
                    return data
                else:
                    return []
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save(self, data: list):
        """
        保存数据到JSON文件（带文件锁）
        
        Args:
            data: 要保存的数据列表
        """
        with self._lock:
            # 使用标准格式包装数据
            wrapper = {
                "metadata": {
                    "entity_type": self.__class__.__name__,
                    "version": 1,
                    "last_updated": self._get_timestamp(),
                    "record_count": len(data)
                },
                "records": data
            }
            
            # 先写入临时文件，然后原子替换
            temp_path = self.filepath + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(wrapper, f, ensure_ascii=False, indent=2)
            
            # 原子替换（尽可能保证数据完整性）
            os.replace(temp_path, self.filepath)
    
    def _generate_id(self, prefix: str = "id") -> str:
        """
        生成带前缀的唯一ID（UUID v4）
        
        Args:
            prefix: ID前缀
        
        Returns:
            str: 生成的ID，格式：prefix_{uuid}
        """
        return f"{prefix}_{uuid.uuid4().hex}"
    
    def _get_timestamp(self) -> str:
        """
        获取当前UTC时间戳（ISO 8601格式）
        
        Returns:
            str: ISO 8601格式的时间戳，如 "2026-04-15T10:30:00Z"
        """
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def create(self, item: dict) -> dict:
        """
        创建记录
        
        自动添加以下字段：
        - id: 唯一标识（如果不存在）
        - created_at: 创建时间
        - updated_at: 更新时间
        - deleted_at: 软删除标记（初始为null）
        
        Args:
            item: 要创建的数据项
        
        Returns:
            dict: 创建后的完整记录（包含自动生成的字段）
        """
        # 复制数据，避免修改原始对象
        record = item.copy()
        
        # 自动生成ID（如果未提供）
        if 'id' not in record or not record['id']:
            # 根据实体类型推断前缀
            prefix = self._get_id_prefix()
            record['id'] = self._generate_id(prefix)
        
        # 添加时间戳
        now = self._get_timestamp()
        record['created_at'] = now
        record['updated_at'] = now
        record['deleted_at'] = None
        
        # 加载现有数据并追加
        data = self._load()
        data.append(record)
        self._save(data)
        
        return record
    
    def get(self, item_id: str) -> Optional[dict]:
        """
        按ID获取单条记录
        
        注意：此方法会过滤已软删除的记录
        
        Args:
            item_id: 记录ID
        
        Returns:
            dict | None: 找到的记录，不存在或已删除返回None
        """
        data = self._load()
        for item in data:
            if item.get('id') == item_id and item.get('deleted_at') is None:
                return item.copy()
        return None
    
    def get_by_id(self, item_id: str, include_deleted: bool = False) -> Optional[dict]:
        """
        按ID获取记录（可包含已删除记录）
        
        Args:
            item_id: 记录ID
            include_deleted: 是否包含已软删除的记录
        
        Returns:
            dict | None: 找到的记录
        """
        data = self._load()
        for item in data:
            if item.get('id') == item_id:
                if include_deleted or item.get('deleted_at') is None:
                    return item.copy()
        return None
    
    def update(self, item_id: str, updates: dict) -> Optional[dict]:
        """
        更新记录
        
        自动更新updated_at字段，保留created_at不变
        
        Args:
            item_id: 要更新的记录ID
            updates: 更新的字段字典
        
        Returns:
            dict | None: 更新后的记录，记录不存在返回None
        """
        data = self._load()
        
        for i, item in enumerate(data):
            if item.get('id') == item_id and item.get('deleted_at') is None:
                # 更新字段（保留id和created_at）
                for key, value in updates.items():
                    if key not in ['id', 'created_at']:
                        data[i][key] = value
                
                # 更新时间戳
                data[i]['updated_at'] = self._get_timestamp()
                
                self._save(data)
                return data[i].copy()
        
        return None
    
    def delete(self, item_id: str, soft_delete: bool = True) -> bool:
        """
        删除记录
        
        支持软删除（默认）和硬删除
        
        Args:
            item_id: 要删除的记录ID
            soft_delete: 是否软删除（True=标记删除，False=物理删除）
        
        Returns:
            bool: 删除是否成功
        """
        data = self._load()
        
        for i, item in enumerate(data):
            if item.get('id') == item_id:
                if soft_delete:
                    # 软删除：设置deleted_at时间戳
                    data[i]['deleted_at'] = self._get_timestamp()
                    data[i]['updated_at'] = data[i]['deleted_at']
                else:
                    # 硬删除：从列表中移除
                    data.pop(i)
                
                self._save(data)
                return True
        
        return False
    
    def restore(self, item_id: str) -> Optional[dict]:
        """
        恢复已软删除的记录
        
        Args:
            item_id: 要恢复的记录ID
        
        Returns:
            dict | None: 恢复后的记录，记录不存在或未删除返回None
        """
        data = self._load()
        
        for i, item in enumerate(data):
            if item.get('id') == item_id and item.get('deleted_at') is not None:
                data[i]['deleted_at'] = None
                data[i]['updated_at'] = self._get_timestamp()
                
                self._save(data)
                return data[i].copy()
        
        return None
    
    def list(self, 
             filters: dict = None, 
             page: int = 1, 
             page_size: int = 20, 
             sort_by: str = 'created_at', 
             sort_order: str = 'desc',
             include_deleted: bool = False) -> dict:
        """
        列表查询，支持过滤、分页、排序
        
        Args:
            filters: 过滤条件字典，如 {"status": "active"}
            page: 页码（从1开始）
            page_size: 每页条数
            sort_by: 排序字段
            sort_order: 排序方向（asc/desc）
            include_deleted: 是否包含已删除记录
        
        Returns:
            dict: 分页结果
            {
                "items": [...],      # 当前页数据
                "total": N,          # 总记录数
                "page": N,           # 当前页码
                "page_size": N,      # 每页条数
                "total_pages": N     # 总页数
            }
        """
        data = self._load()
        
        # 过滤已删除记录
        if not include_deleted:
            data = [item for item in data if item.get('deleted_at') is None]
        
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if value is not None:
                    data = [item for item in data if item.get(key) == value]
        
        # 排序
        reverse = sort_order.lower() == 'desc'
        data = sorted(
            data, 
            key=lambda x: x.get(sort_by, ''), 
            reverse=reverse
        )
        
        # 计算分页
        total = len(data)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        
        # 截取当前页数据
        start = (page - 1) * page_size
        end = start + page_size
        items = data[start:end]
        
        return {
            "items": [item.copy() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def search(self, keyword: str, fields: list = None) -> list:
        """
        按关键词搜索指定字段
        
        支持多字段模糊搜索，不区分大小写
        
        Args:
            keyword: 搜索关键词
            fields: 要搜索的字段列表，默认为 ['name', 'title', 'content']
        
        Returns:
            list: 匹配的记录列表
        """
        if not keyword:
            return []
        
        if fields is None:
            fields = ['name', 'title', 'content']
        
        data = self._load()
        keyword_lower = keyword.lower()
        
        results = []
        for item in data:
            # 跳过已删除记录
            if item.get('deleted_at') is not None:
                continue
            
            # 在指定字段中搜索
            for field in fields:
                value = item.get(field, '')
                if value and keyword_lower in str(value).lower():
                    results.append(item.copy())
                    break  # 找到一个匹配就停止
        
        return results
    
    def count(self, filters: dict = None, include_deleted: bool = False) -> int:
        """
        统计记录数量
        
        Args:
            filters: 过滤条件
            include_deleted: 是否包含已删除记录
        
        Returns:
            int: 记录数量
        """
        data = self._load()
        
        if not include_deleted:
            data = [item for item in data if item.get('deleted_at') is None]
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    data = [item for item in data if item.get(key) == value]
        
        return len(data)
    
    def exists(self, item_id: str, include_deleted: bool = False) -> bool:
        """
        检查记录是否存在
        
        Args:
            item_id: 记录ID
            include_deleted: 是否包含已删除记录
        
        Returns:
            bool: 记录是否存在
        """
        return self.get_by_id(item_id, include_deleted) is not None
    
    def _get_id_prefix(self) -> str:
        """
        获取ID前缀
        
        子类可以重写此方法以提供特定前缀
        
        Returns:
            str: ID前缀
        """
        # 从文件名推断前缀
        filename = self.filename.lower()
        prefix_map = {
            'qa_records': 'qa',
            'knowledge_base': 'kb',
            'complaints': 'tk',
            'quality_checks': 'qc',
            'customer_profiles': 'cp',
            'anomaly_alerts': 'alt',
            'reports': 'rpt',
            'churn_risks': 'cr',
            'education_content': 'edu',
            'sentiment_records': 'sen',
            'competitor_analysis': 'ca',
            'event_plans': 'ep',
            'care_records': 'care',
            'system_config': 'cfg'
        }
        
        for key, prefix in prefix_map.items():
            if key in filename:
                return prefix
        
        return 'id'
