import { useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import './Header.css'

// 面包屑映射
const breadcrumbMap = {
  '/': [{ label: '主控台', path: '/' }],
  '/cs/qa': [{ label: '主控台', path: '/' }, { label: '智能问答', path: '/cs/qa' }],
  '/cs/knowledge': [{ label: '主控台', path: '/' }, { label: '知识库管理', path: '/cs/knowledge' }],
  '/cs/complaint': [{ label: '主控台', path: '/' }, { label: '投诉管理', path: '/cs/complaint' }],
  '/cs/script': [{ label: '主控台', path: '/' }, { label: '话术生成', path: '/cs/script' }],
  '/cs/quality': [{ label: '主控台', path: '/' }, { label: '质检管理', path: '/cs/quality' }],
  '/cs/training': [{ label: '主控台', path: '/' }, { label: '培训管理', path: '/cs/training' }],
  '/hnw': [{ label: '主控台', path: '/' }, { label: '高净值客户服务', path: '/hnw' }],
  '/analytics': [{ label: '主控台', path: '/' }, { label: '数据分析与洞察', path: '/analytics' }],
  '/education': [{ label: '主控台', path: '/' }, { label: '投教与合规', path: '/education' }],
  '/market': [{ label: '主控台', path: '/' }, { label: '市场监测', path: '/market' }]
}

function Header() {
  const location = useLocation()
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const breadcrumbs = breadcrumbMap[location.pathname] || [{ label: '主控台', path: '/' }]

  // 模拟通知数据
  const notifications = [
    { id: 1, type: 'warning', message: '有新的投诉工单待处理', time: '5分钟前' },
    { id: 2, type: 'info', message: '系统将于今晚进行维护', time: '1小时前' },
    { id: 3, type: 'success', message: '质检报告已生成', time: '2小时前' }
  ]

  return (
    <header className="header">
      {/* 面包屑导航 */}
      <nav className="breadcrumb">
        {breadcrumbs.map((item, index) => (
          <span key={item.path} className="breadcrumb-item">
            {index > 0 && <span className="breadcrumb-separator">/</span>}
            {index === breadcrumbs.length - 1 ? (
              <span className="breadcrumb-current">{item.label}</span>
            ) : (
              <Link to={item.path} className="breadcrumb-link">{item.label}</Link>
            )}
          </span>
        ))}
      </nav>

      {/* 右侧操作区 */}
      <div className="header-actions">
        {/* LLM状态芯片 */}
        <div className="llm-status">
          <span className="llm-status-dot online"></span>
          <span className="llm-status-text">AI服务正常</span>
        </div>

        {/* 通知 */}
        <div className="header-action notification-wrapper">
          <button 
            className="action-btn"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <span className="action-icon">🔔</span>
            <span className="notification-badge">3</span>
          </button>
          
          {showNotifications && (
            <div className="notification-dropdown">
              <div className="notification-header">
                <span>系统通知</span>
                <button className="mark-read">全部已读</button>
              </div>
              <div className="notification-list">
                {notifications.map(n => (
                  <div key={n.id} className={`notification-item ${n.type}`}>
                    <span className="notification-dot"></span>
                    <div className="notification-content">
                      <p className="notification-message">{n.message}</p>
                      <span className="notification-time">{n.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 用户菜单 */}
        <div className="header-action user-menu-wrapper">
          <button 
            className="action-btn user-btn"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <span className="user-avatar-small">👤</span>
            <span className="user-name-text">客服代表</span>
            <span className="dropdown-arrow">▼</span>
          </button>
          
          {showUserMenu && (
            <div className="user-dropdown">
              <div className="user-dropdown-header">
                <span className="user-avatar-small">👤</span>
                <div>
                  <div className="dropdown-user-name">客服代表</div>
                  <div className="dropdown-user-role">客户关系部</div>
                </div>
              </div>
              <div className="user-dropdown-divider"></div>
              <button className="dropdown-item">
                <span>⚙️</span> 个人设置
              </button>
              <button className="dropdown-item">
                <span>🚪</span> 退出登录
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
