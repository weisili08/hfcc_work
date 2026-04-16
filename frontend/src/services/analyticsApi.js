import api from './api'

/**
 * F3 数据分析与洞察模块 API
 * Data Analytics APIs
 */

// 客户画像分析
export const analyzePortrait = (data) => api.post('/analytics/portrait', data)

// 异常交易识别
export const detectAnomaly = (data) => api.post('/analytics/anomaly', data)

// 报表生成
export const generateReport = (data) => api.post('/analytics/report', data)

// 流失风险预警
export const getChurnRisk = (params) => api.get('/analytics/churn-risk', { params })

// 获取分析历史记录
export const getAnalyticsHistory = (params) => api.get('/analytics/history', { params })

// 获取单个分析报告
export const getAnalyticsReportById = (reportId) => api.get(`/analytics/reports/${reportId}`)

// 获取异常告警列表
export const getAnomalyAlerts = (params) => api.get('/analytics/anomaly/alerts', { params })

// 更新异常告警状态
export const updateAnomalyAlertStatus = (alertId, data) => api.put(`/analytics/anomaly/alerts/${alertId}/status`, data)

// 获取流失风险客户详情
export const getChurnRiskDetail = (customerId) => api.get(`/analytics/churn-risk/${customerId}`)

// 生成挽留建议
export const generateRetentionPlan = (data) => api.post('/analytics/churn-risk/retention-plan', data)
