import api from './api'

/**
 * F1 客户服务管理模块 API
 * Customer Service Management APIs
 */

// ========== 智能问答 ==========
// 智能客服问答
export const qaChat = (data) => api.post('/cs/ask', data)

// 获取会话列表
export const getQASessions = () => api.get('/cs/qa/sessions')

// 创建新会话
export const createQASession = (data) => api.post('/cs/qa/sessions', data)

// 删除会话
export const deleteQASession = (sessionId) => api.delete(`/cs/qa/sessions/${sessionId}`)

// ========== 知识库管理 ==========
// 知识库查询
export const getKnowledge = (params) => api.get('/cs/knowledge', { params })

// 获取单个知识库文档
export const getKnowledgeById = (kbId) => api.get(`/cs/knowledge/${kbId}`)

// 创建知识库条目
export const createKnowledge = (data) => api.post('/cs/knowledge', data)

// 知识库更新
export const updateKnowledge = (data) => api.put('/cs/knowledge', data)

// 删除知识库条目
export const deleteKnowledge = (kbId) => api.delete(`/cs/knowledge/${kbId}`)

// ========== 话术生成 ==========
// 话术生成
export const generateSpeech = (data) => api.post('/cs/speech/generate', data)

// 获取话术历史
export const getSpeechHistory = (params) => api.get('/cs/speech/history', { params })

// ========== 质检管理 ==========
// 通话质检分析
export const analyzeQuality = (data) => api.post('/cs/quality/analyze', data)

// 获取质检记录列表
export const getQualityRecords = (params) => api.get('/cs/quality/records', { params })

// 获取单个质检记录
export const getQualityRecordById = (recordId) => api.get(`/cs/quality/records/${recordId}`)

// ========== 培训管理 ==========
// 培训内容生成
export const generateTraining = (data) => api.post('/cs/training/generate', data)

// 获取培训课程列表
export const getTrainings = (params) => api.get('/cs/training', { params })

// 获取单个培训课程
export const getTrainingById = (trainingId) => api.get(`/cs/training/${trainingId}`)

// ========== 投诉管理 ==========
// 投诉提交
export const submitComplaint = (data) => api.post('/cs/complaint', data)

// 投诉列表查询
export const getComplaints = (params) => api.get('/cs/complaints', { params })

// 获取单个投诉
export const getComplaintById = (ticketId) => api.get(`/cs/complaints/${ticketId}`)

// 更新投诉状态
export const updateComplaintStatus = (ticketId, data) => api.put(`/cs/complaints/${ticketId}/status`, data)

// 分配投诉处理人
export const assignComplaint = (ticketId, data) => api.put(`/cs/complaints/${ticketId}/assign`, data)
