/**
 * 工具函数
 * Helper Functions
 */

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式模板
 * @returns {string}
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm') {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化数字（千分位）
 * @param {number} num - 数字
 * @param {number} decimals - 小数位数
 * @returns {string}
 */
export function formatNumber(num, decimals = 0) {
  if (num === null || num === undefined) return '-'
  
  const n = Number(num)
  if (isNaN(n)) return '-'
  
  return n.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 格式化百分比
 * @param {number} value - 数值（0-1）
 * @param {number} decimals - 小数位数
 * @returns {string}
 */
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined) return '-'
  
  const n = Number(value)
  if (isNaN(n)) return '-'
  
  return (n * 100).toFixed(decimals) + '%'
}

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @param {string} currency - 货币符号
 * @returns {string}
 */
export function formatCurrency(amount, currency = '¥') {
  if (amount === null || amount === undefined) return '-'
  
  const n = Number(amount)
  if (isNaN(n)) return '-'
  
  return currency + formatNumber(n, 2)
}

/**
 * 截断文本
 * @param {string} text - 文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 后缀
 * @returns {string}
 */
export function truncateText(text, maxLength = 100, suffix = '...') {
  if (!text) return ''
  if (text.length <= maxLength) return text
  
  return text.slice(0, maxLength) + suffix
}

/**
 * 生成唯一ID
 * @param {string} prefix - 前缀
 * @returns {string}
 */
export function generateId(prefix = 'id') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 防抖函数
 * @param {Function} fn - 函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function}
 */
export function debounce(fn, delay = 300) {
  let timer = null
  
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function}
 */
export function throttle(fn, limit = 300) {
  let inThrottle = false
  
  return function (...args) {
    if (!inThrottle) {
      fn.apply(this, args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

/**
 * 计算SLA剩余时间
 * @param {string} deadline - 截止时间
 * @returns {object}
 */
export function calculateSLA(deadline) {
  if (!deadline) return { hours: 0, status: 'unknown' }
  
  const now = new Date()
  const end = new Date(deadline)
  const diffMs = end - now
  const diffHours = Math.ceil(diffMs / (1000 * 60 * 60))
  
  let status = 'normal'
  if (diffHours <= 0) status = 'overdue'
  else if (diffHours <= 4) status = 'urgent'
  else if (diffHours <= 24) status = 'warning'
  
  return { hours: diffHours, status }
}

/**
 * 脱敏手机号
 * @param {string} phone - 手机号
 * @returns {string}
 */
export function maskPhone(phone) {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 脱敏身份证号
 * @param {string} idCard - 身份证号
 * @returns {string}
 */
export function maskIdCard(idCard) {
  if (!idCard || idCard.length !== 18) return idCard
  return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
}

/**
 * 深拷贝
 * @param {any} obj - 对象
 * @returns {any}
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const copy = {}
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone(obj[key])
    })
    return copy
  }
  return obj
}

/**
 * 判断对象是否为空
 * @param {object} obj - 对象
 * @returns {boolean}
 */
export function isEmptyObject(obj) {
  return Object.keys(obj).length === 0
}

/**
 * 获取文件扩展名
 * @param {string} filename - 文件名
 * @returns {string}
 */
export function getFileExtension(filename) {
  if (!filename) return ''
  const parts = filename.split('.')
  return parts.length > 1 ? parts.pop().toLowerCase() : ''
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
