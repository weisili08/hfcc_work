import { useNavigate } from 'react-router-dom'
import './Dashboard.css'

// 模拟数据 - 关键业务指标
const mockStats = [
  {
    id: 'consultation',
    title: '今日咨询量',
    value: 128,
    change: '+12.5%',
    changeType: 'positive',
    icon: '💬',
    color: '#3182ce',
    path: '/cs/qa'
  },
  {
    id: 'complaint',
    title: '投诉处理中',
    value: 23,
    change: '5个紧急',
    changeType: 'warning',
    icon: '📝',
    color: '#dd6b20',
    path: '/cs/complaint'
  },
  {
    id: 'hnw',
    title: '高净值客户',
    value: 456,
    change: '+8位新增',
    changeType: 'positive',
    icon: '💎',
    color: '#805ad5',
    path: '/hnw'
  },
  {
    id: 'sentiment',
    title: '舆情预警',
    value: 3,
    change: '2个负面',
    changeType: 'negative',
    icon: '⚠️',
    color: '#e53e3e',
    path: '/market'
  }
]

// 模拟数据 - 各模块快捷入口
const quickAccess = [
  {
    id: 'qa',
    title: '智能问答',
    description: '基于知识库的自然语言问答',
    icon: '💬',
    color: '#3182ce',
    path: '/cs/qa'
  },
  {
    id: 'knowledge',
    title: '知识库管理',
    description: '知识条目管理与维护',
    icon: '📚',
    color: '#38a169',
    path: '/cs/knowledge'
  },
  {
    id: 'complaint',
    title: '投诉管理',
    description: '工单创建与状态跟踪',
    icon: '📝',
    color: '#dd6b20',
    path: '/cs/complaint'
  },
  {
    id: 'script',
    title: '话术生成',
    description: 'AI生成标准化话术',
    icon: '🎤',
    color: '#805ad5',
    path: '/cs/script'
  },
  {
    id: 'quality',
    title: '质检管理',
    description: '通话录音质检分析',
    icon: '✅',
    color: '#d69e2e',
    path: '/cs/quality'
  },
  {
    id: 'training',
    title: '培训管理',
    description: 'AI陪练与培训考核',
    icon: '📖',
    color: '#00b5d8',
    path: '/cs/training'
  }
]

// 模拟数据 - 待办事项
const todoList = [
  {
    id: 1,
    type: 'complaint',
    title: '处理客户投诉工单',
    description: 'TK-20260416-0012 基金赎回问题',
    priority: 'high',
    time: '2小时前'
  },
  {
    id: 2,
    type: 'hnw',
    title: '高净值客户关怀',
    description: '客户张**生日关怀提醒',
    priority: 'medium',
    time: '今天'
  },
  {
    id: 3,
    type: 'training',
    title: '完成合规培训',
    description: '反洗钱培训模块待完成',
    priority: 'medium',
    time: '明天截止'
  },
  {
    id: 4,
    type: 'quality',
    title: '质检报告审核',
    description: '昨日通话录音质检结果',
    priority: 'low',
    time: '3小时前'
  }
]

// 模拟数据 - 咨询趋势（近7天）
const trendData = [
  { day: '周一', value: 95 },
  { day: '周二', value: 112 },
  { day: '周三', value: 108 },
  { day: '周四', value: 125 },
  { day: '周五', value: 138 },
  { day: '周六', value: 89 },
  { day: '周日', value: 76 }
]

function Dashboard() {
  const navigate = useNavigate()

  const handleStatClick = (path) => {
    navigate(path)
  }

  const handleQuickAccessClick = (path) => {
    navigate(path)
  }

  const getPriorityLabel = (priority) => {
    const map = {
      high: { label: '紧急', color: '#e53e3e' },
      medium: { label: '普通', color: '#d69e2e' },
      low: { label: '低', color: '#38a169' }
    }
    return map[priority] || map.low
  }

  const getTodoIcon = (type) => {
    const map = {
      complaint: '📝',
      hnw: '💎',
      training: '📖',
      quality: '✅'
    }
    return map[type] || '📋'
  }

  // 计算趋势最大值用于图表缩放
  const maxTrendValue = Math.max(...trendData.map(d => d.value))

  return (
    <div className="dashboard">
      {/* 页面标题 */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">主控台</h1>
        <p className="dashboard-subtitle">欢迎回来，今日工作概览</p>
      </div>

      {/* 关键业务指标 */}
      <div className="stats-grid">
        {mockStats.map(stat => (
          <div 
            key={stat.id} 
            className="stat-card"
            onClick={() => handleStatClick(stat.path)}
            style={{ cursor: 'pointer' }}
          >
            <div className="stat-icon" style={{ backgroundColor: `${stat.color}20`, color: stat.color }}>
              {stat.icon}
            </div>
            <div className="stat-content">
              <div className="stat-title">{stat.title}</div>
              <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
              <div className={`stat-change ${stat.changeType}`}>
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 主内容区 */}
      <div className="dashboard-main">
        {/* 左侧：快捷入口 + 趋势图 */}
        <div className="dashboard-left">
          {/* 快捷入口 */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">快捷入口</h2>
            </div>
            <div className="quick-access-grid">
              {quickAccess.map(item => (
                <div 
                  key={item.id}
                  className="quick-access-card"
                  onClick={() => handleQuickAccessClick(item.path)}
                >
                  <div className="quick-access-icon" style={{ backgroundColor: `${item.color}15`, color: item.color }}>
                    {item.icon}
                  </div>
                  <div className="quick-access-content">
                    <div className="quick-access-title">{item.title}</div>
                    <div className="quick-access-desc">{item.description}</div>
                  </div>
                  <div className="quick-access-arrow">→</div>
                </div>
              ))}
            </div>
          </div>

          {/* 咨询趋势 */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">咨询量趋势（近7天）</h2>
              <span className="section-subtitle">总计：{trendData.reduce((sum, d) => sum + d.value, 0)} 次咨询</span>
            </div>
            <div className="trend-chart">
              <div className="trend-bars">
                {trendData.map((item, index) => (
                  <div key={index} className="trend-bar-item">
                    <div className="trend-bar-wrapper">
                      <div 
                        className="trend-bar"
                        style={{ 
                          height: `${(item.value / maxTrendValue) * 100}%`,
                          backgroundColor: index === trendData.length - 1 ? '#3182ce' : '#90cdf4'
                        }}
                      >
                        <span className="trend-bar-value">{item.value}</span>
                      </div>
                    </div>
                    <div className="trend-bar-label">{item.day}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：待办事项 */}
        <div className="dashboard-right">
          <div className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">待办事项</h2>
              <span className="todo-count">{todoList.length} 项待处理</span>
            </div>
            <div className="todo-list">
              {todoList.map(todo => {
                const priority = getPriorityLabel(todo.priority)
                return (
                  <div key={todo.id} className="todo-item">
                    <div className="todo-icon">{getTodoIcon(todo.type)}</div>
                    <div className="todo-content">
                      <div className="todo-title-row">
                        <span className="todo-title">{todo.title}</span>
                        <span 
                          className="todo-priority"
                          style={{ backgroundColor: `${priority.color}20`, color: priority.color }}
                        >
                          {priority.label}
                        </span>
                      </div>
                      <div className="todo-description">{todo.description}</div>
                      <div className="todo-time">{todo.time}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 系统状态 */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">系统状态</h2>
            </div>
            <div className="system-status">
              <div className="status-item">
                <span className="status-dot online"></span>
                <span className="status-label">AI问答服务</span>
                <span className="status-value">正常</span>
              </div>
              <div className="status-item">
                <span className="status-dot online"></span>
                <span className="status-label">知识库服务</span>
                <span className="status-value">正常</span>
              </div>
              <div className="status-item">
                <span className="status-dot online"></span>
                <span className="status-label">质检分析服务</span>
                <span className="status-value">正常</span>
              </div>
              <div className="status-item">
                <span className="status-dot warning"></span>
                <span className="status-label">舆情采集服务</span>
                <span className="status-value">延迟</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
