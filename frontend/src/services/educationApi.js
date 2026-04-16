import api from './api'

/**
 * F4 投资者教育与合规模块 API
 * Education & Compliance APIs
 */

// 投教内容生成
export const generateEducationContent = (data) => api.post('/education/content', data)

// 反洗钱检查
export const amlCheck = (data) => api.post('/compliance/aml-check', data)

// 合规风险提示
export const getRiskTips = (params) => api.get('/compliance/risk-tips', { params })

// 获取投教内容列表
export const getEducationContents = (params) => api.get('/education/contents', { params })

// 获取单个投教内容
export const getEducationContentById = (contentId) => api.get(`/education/contents/${contentId}`)

// 保存投教内容
export const saveEducationContent = (data) => api.post('/education/contents', data)

// 更新投教内容
export const updateEducationContent = (contentId, data) => api.put(`/education/contents/${contentId}`, data)

// 删除投教内容
export const deleteEducationContent = (contentId) => api.delete(`/education/contents/${contentId}`)

// 内容合规检查
export const checkContentCompliance = (data) => api.post('/compliance/content-check', data)

// 获取合规检查历史
export const getComplianceHistory = (params) => api.get('/compliance/history', { params })
