import api from './api'

/**
 * F5 市场监测与产品研究模块 API
 * Market Monitoring APIs
 */

// 舆情监控
export const getSentiment = (params) => api.get('/market/sentiment', { params })

// 竞品分析
export const analyzeCompetitor = (data) => api.post('/market/competitor', data)

// 市场动态
export const getMarketTrends = (params) => api.get('/market/trends', { params })

// 获取舆情详情
export const getSentimentById = (mentionId) => api.get(`/market/sentiment/${mentionId}`)

// 获取竞品分析历史
export const getCompetitorAnalysisHistory = (params) => api.get('/market/competitor/history', { params })

// 获取产品对比数据
export const getProductComparison = (params) => api.get('/market/products/comparison', { params })

// 获取市场趋势详情
export const getMarketTrendById = (trendId) => api.get(`/market/trends/${trendId}`)

// 订阅舆情关键词
export const subscribeSentimentKeywords = (data) => api.post('/market/sentiment/subscribe', data)

// 获取订阅的关键词列表
export const getSubscribedKeywords = () => api.get('/market/sentiment/keywords')
