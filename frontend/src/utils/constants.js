/**
 * 常量定义
 * Constants
 */

// 投诉紧急程度
export const URGENCY_LEVELS = {
  P0: { label: '紧急', color: '#e53e3e', hours: 24 },
  P1: { label: '高', color: '#dd6b20', hours: 48 },
  P2: { label: '中', color: '#d69e2e', hours: 72 },
  P3: { label: '低', color: '#38a169', hours: 120 }
}

// 投诉类型
export const COMPLAINT_TYPES = {
  product: '产品相关',
  service: '服务相关',
  system: '系统相关',
  staff: '人员相关',
  other: '其他'
}

// 工单状态
export const TICKET_STATUS = {
  pending: { label: '待处理', color: '#d69e2e' },
  processing: { label: '处理中', color: '#3182ce' },
  escalated: { label: '已升级', color: '#805ad5' },
  resolved: { label: '已解决', color: '#38a169' },
  closed: { label: '已关闭', color: '#718096' }
}

// 风险等级
export const RISK_LEVELS = {
  high: { label: '高风险', color: '#e53e3e' },
  medium: { label: '中风险', color: '#d69e2e' },
  low: { label: '低风险', color: '#38a169' }
}

// 客户风险等级 C1-C5
export const CUSTOMER_RISK_LEVELS = {
  C1: { label: '保守型', description: '低风险承受能力' },
  C2: { label: '稳健型', description: '中低风险承受能力' },
  C3: { label: '平衡型', description: '中等风险承受能力' },
  C4: { label: '积极型', description: '中高风险承受能力' },
  C5: { label: '激进型', description: '高风险承受能力' }
}

// 话术场景
export const SPEECH_SCENARIOS = {
  comfort: { label: '安抚', icon: '🤗' },
  explain: { label: '解释', icon: '📋' },
  guide: { label: '引导', icon: '👉' },
  apologize: { label: '致歉', icon: '🙏' },
  recommend: { label: '推荐', icon: '⭐' }
}

// 质检维度
export const QUALITY_DIMENSIONS = {
  service_attitude: { label: '服务态度', weight: 30 },
  compliance: { label: '合规用语', weight: 30 },
  communication: { label: '沟通技巧', weight: 25 },
  problem_solving: { label: '问题解决', weight: 15 }
}

// 情感分析结果
export const SENTIMENT_TYPES = {
  positive: { label: '正面', color: '#38a169' },
  neutral: { label: '中性', color: '#718096' },
  negative: { label: '负面', color: '#e53e3e' }
}

// 培训类型
export const TRAINING_TYPES = {
  product: { label: '产品知识' },
  complaint: { label: '投诉处理' },
  difficult: { label: '疑难问题' },
  compliance: { label: '合规培训' }
}

// 分页默认值
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
}

// 本地存储键名
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed'
}

// API 错误码
export const ERROR_CODES = {
  INVALID_REQUEST: '请求参数错误',
  INVALID_QUERY: '查询内容无效',
  INVALID_SESSION: '会话无效',
  UNAUTHORIZED: '未授权',
  FORBIDDEN: '无权限访问',
  NOT_FOUND: '资源不存在',
  INTERNAL_ERROR: '服务器内部错误',
  SERVICE_UNAVAILABLE: '服务不可用',
  LLM_UNAVAILABLE: 'AI服务暂时不可用'
}
