import api from './api'

/**
 * F2 高净值客户服务模块 API
 * High Net Worth Service APIs
 */

// 资产配置建议
export const getAllocationAdvice = (data) => api.post('/hnw/allocation', data)

// 关怀计划生成
export const generateCarePlan = (data) => api.post('/hnw/care/plan', data)

// 活动策划
export const generateEventPlan = (data) => api.post('/hnw/event/plan', data)

// 触达节点查询
export const getTouchpoints = (params) => api.get('/hnw/touchpoints', { params })

// 获取高净值客户列表
export const getHNWCustomers = (params) => api.get('/hnw/customers', { params })

// 获取单个客户详情
export const getHNWCustomerById = (customerId) => api.get(`/hnw/customers/${customerId}`)

// 获取客户资产详情
export const getCustomerAssets = (customerId) => api.get(`/hnw/customers/${customerId}/assets`)

// 更新客户关怀任务状态
export const updateCareTaskStatus = (taskId, data) => api.put(`/hnw/care/tasks/${taskId}/status`, data)

// 获取活动列表
export const getEvents = (params) => api.get('/hnw/events', { params })

// 获取单个活动详情
export const getEventById = (eventId) => api.get(`/hnw/events/${eventId}`)
