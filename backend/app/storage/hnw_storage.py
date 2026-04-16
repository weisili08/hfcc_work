"""
高净值客户存储层模块
提供高净值客户、服务记录、活动记录的存储管理
"""

from typing import Optional, List
from app.storage.base_storage import BaseStorage


class HNWCustomerStorage(BaseStorage):
    """
    高净值客户存储类
    
    字段：
    - id: 客户唯一标识
    - name: 客户姓名
    - phone: 联系电话
    - email: 邮箱
    - risk_level: 风险等级 (conservative/moderate/aggressive)
    - aum: 资产管理规模
    - tier: 客户等级 (diamond/platinum/gold)
    - manager_id: 客户经理ID
    - tags: 标签列表
    - preferences: 偏好设置
    - status: 状态 (active/inactive)
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, 'hnw_customers.json')
    
    def _get_id_prefix(self) -> str:
        return 'hnw'
    
    def get_by_tier(self, tier: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按客户等级查询
        
        Args:
            tier: 客户等级 (diamond/platinum/gold)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(filters={'tier': tier}, page=page, page_size=page_size)
    
    def get_by_risk_level(self, risk_level: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按风险等级查询
        
        Args:
            risk_level: 风险等级 (conservative/moderate/aggressive)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(filters={'risk_level': risk_level}, page=page, page_size=page_size)
    
    def get_by_manager(self, manager_id: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按客户经理查询
        
        Args:
            manager_id: 客户经理ID
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(filters={'manager_id': manager_id}, page=page, page_size=page_size)
    
    def search_by_tags(self, tags: List[str]) -> List[dict]:
        """
        按标签搜索客户
        
        Args:
            tags: 标签列表
        
        Returns:
            List[dict]: 匹配的客户列表
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            item_tags = item.get('tags', [])
            if any(tag in item_tags for tag in tags):
                results.append(item.copy())
        
        return results
    
    def update_aum(self, customer_id: str, new_aum: float) -> Optional[dict]:
        """
        更新客户AUM
        
        Args:
            customer_id: 客户ID
            new_aum: 新的资产管理规模
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(customer_id, {'aum': new_aum})
    
    def update_tier(self, customer_id: str, new_tier: str) -> Optional[dict]:
        """
        更新客户等级
        
        Args:
            customer_id: 客户ID
            new_tier: 新的客户等级 (diamond/platinum/gold)
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(customer_id, {'tier': new_tier})


class HNWServiceStorage(BaseStorage):
    """
    高净值客户服务记录存储类
    
    字段：
    - id: 记录唯一标识
    - customer_id: 客户ID
    - service_type: 服务类型 (consultation/allocation/review/care)
    - description: 服务描述
    - result: 服务结果
    - next_action: 后续行动
    - created_by: 创建人
    - created_at: 创建时间
    """
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, 'hnw_services.json')
    
    def _get_id_prefix(self) -> str:
        return 'svc'
    
    def get_by_customer(self, customer_id: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按客户查询服务记录
        
        Args:
            customer_id: 客户ID
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'customer_id': customer_id},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def get_by_service_type(self, service_type: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按服务类型查询
        
        Args:
            service_type: 服务类型 (consultation/allocation/review/care)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'service_type': service_type},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )
    
    def get_by_creator(self, created_by: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按创建人查询
        
        Args:
            created_by: 创建人ID
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'created_by': created_by},
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order='desc'
        )


class HNWEventStorage(BaseStorage):
    """
    高净值客户活动记录存储类
    
    字段：
    - id: 活动唯一标识
    - title: 活动标题
    - type: 活动类型 (online/offline/mixed)
    - description: 活动描述
    - target_tier: 目标客户等级
    - date: 活动日期
    - location: 活动地点
    - budget: 预算
    - status: 状态 (planning/confirmed/completed/cancelled)
    - attendees: 参与者列表
    - effect_score: 效果评分
    - created_by: 创建人
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, 'hnw_events.json')
    
    def _get_id_prefix(self) -> str:
        return 'evt'
    
    def get_by_status(self, status: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按状态查询活动
        
        Args:
            status: 状态 (planning/confirmed/completed/cancelled)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'status': status},
            page=page,
            page_size=page_size,
            sort_by='date',
            sort_order='asc'
        )
    
    def get_by_type(self, event_type: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按活动类型查询
        
        Args:
            event_type: 活动类型 (online/offline/mixed)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'type': event_type},
            page=page,
            page_size=page_size,
            sort_by='date',
            sort_order='asc'
        )
    
    def get_by_target_tier(self, tier: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按目标客户等级查询
        
        Args:
            tier: 客户等级 (diamond/platinum/gold)
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            
            target_tiers = item.get('target_tier', [])
            if tier in target_tiers:
                results.append(item)
        
        # 分页
        total = len(results)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        start = (page - 1) * page_size
        end = start + page_size
        items = results[start:end]
        
        return {
            'items': [item.copy() for item in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }
    
    def add_attendee(self, event_id: str, customer_id: str) -> Optional[dict]:
        """
        添加活动参与者
        
        Args:
            event_id: 活动ID
            customer_id: 客户ID
        
        Returns:
            dict | None: 更新后的记录
        """
        event = self.get(event_id)
        if not event:
            return None
        
        attendees = event.get('attendees', [])
        if customer_id not in attendees:
            attendees.append(customer_id)
            return self.update(event_id, {'attendees': attendees})
        
        return event
    
    def update_status(self, event_id: str, status: str) -> Optional[dict]:
        """
        更新活动状态
        
        Args:
            event_id: 活动ID
            status: 新状态 (planning/confirmed/completed/cancelled)
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(event_id, {'status': status})
    
    def update_effect_score(self, event_id: str, score: float) -> Optional[dict]:
        """
        更新活动效果评分
        
        Args:
            event_id: 活动ID
            score: 效果评分 (0-10)
        
        Returns:
            dict | None: 更新后的记录
        """
        return self.update(event_id, {'effect_score': score})


class HNWTouchpointStorage(BaseStorage):
    """
    高净值客户触达任务存储类
    
    字段：
    - id: 任务唯一标识
    - customer_id: 客户ID
    - touchpoint_type: 触达类型 (birthday/anniversary/market_volatility/redemption/large_redemption/no_contact)
    - event_date: 事件日期
    - days_until: 距离天数
    - status: 状态 (pending/completed/ignored)
    - suggested_action: 建议操作
    - script_template: 话术模板
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, 'hnw_touchpoints.json')
    
    def _get_id_prefix(self) -> str:
        return 'tp'
    
    def get_upcoming(self, days: int = 30, page: int = 1, page_size: int = 20) -> dict:
        """
        获取即将到期的触达任务
        
        Args:
            days: 未来N天内
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        data = self._load()
        results = []
        
        for item in data:
            if item.get('deleted_at') is not None:
                continue
            if item.get('status') != 'pending':
                continue
            
            days_until = item.get('days_until', 999)
            if days_until <= days:
                results.append(item)
        
        # 按距离天数排序
        results = sorted(results, key=lambda x: x.get('days_until', 999))
        
        # 分页
        total = len(results)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        start = (page - 1) * page_size
        end = start + page_size
        items = results[start:end]
        
        return {
            'items': [item.copy() for item in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }
    
    def get_by_customer(self, customer_id: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按客户查询触达任务
        
        Args:
            customer_id: 客户ID
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'customer_id': customer_id},
            page=page,
            page_size=page_size,
            sort_by='days_until',
            sort_order='asc'
        )
    
    def get_by_type(self, touchpoint_type: str, page: int = 1, page_size: int = 20) -> dict:
        """
        按触达类型查询
        
        Args:
            touchpoint_type: 触达类型
            page: 页码
            page_size: 每页条数
        
        Returns:
            dict: 分页结果
        """
        return self.list(
            filters={'touchpoint_type': touchpoint_type},
            page=page,
            page_size=page_size,
            sort_by='days_until',
            sort_order='asc'
        )
    
    def complete_touchpoint(self, touchpoint_id: str, notes: str = None) -> Optional[dict]:
        """
        完成触达任务
        
        Args:
            touchpoint_id: 任务ID
            notes: 完成备注
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {'status': 'completed'}
        if notes:
            updates['completion_notes'] = notes
        return self.update(touchpoint_id, updates)
    
    def ignore_touchpoint(self, touchpoint_id: str, reason: str = None) -> Optional[dict]:
        """
        忽略触达任务
        
        Args:
            touchpoint_id: 任务ID
            reason: 忽略原因
        
        Returns:
            dict | None: 更新后的记录
        """
        updates = {'status': 'ignored'}
        if reason:
            updates['ignore_reason'] = reason
        return self.update(touchpoint_id, updates)
