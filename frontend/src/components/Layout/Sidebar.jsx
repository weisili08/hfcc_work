import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import './Sidebar.css'

// 菜单配置
const menuConfig = [
  {
    key: 'dashboard',
    icon: '🏠',
    label: '主控台',
    path: '/'
  },
  {
    key: 'cs',
    icon: '📞',
    label: '客户服务管理',
    children: [
      { key: 'cs-qa', icon: '💬', label: '智能问答', path: '/cs/qa' },
      { key: 'cs-knowledge', icon: '📚', label: '知识库管理', path: '/cs/knowledge' },
      { key: 'cs-complaint', icon: '📝', label: '投诉管理', path: '/cs/complaint' },
      { key: 'cs-script', icon: '🎤', label: '话术生成', path: '/cs/script' },
      { key: 'cs-quality', icon: '✅', label: '质检管理', path: '/cs/quality' },
      { key: 'cs-training', icon: '📖', label: '培训管理', path: '/cs/training' }
    ]
  },
  {
    key: 'hnw',
    icon: '💎',
    label: '高净值客户服务',
    path: '/hnw'
  },
  {
    key: 'analytics',
    icon: '📊',
    label: '数据分析与洞察',
    path: '/analytics'
  },
  {
    key: 'education',
    icon: '📖',
    label: '投教与合规',
    path: '/education'
  },
  {
    key: 'market',
    icon: '📈',
    label: '市场监测',
    path: '/market'
  }
]

function Sidebar() {
  const location = useLocation()
  const [expandedKeys, setExpandedKeys] = useState(['cs'])

  const toggleMenu = (key) => {
    setExpandedKeys(prev => 
      prev.includes(key) 
        ? prev.filter(k => k !== key)
        : [...prev, key]
    )
  }

  const isMenuActive = (item) => {
    if (item.path === location.pathname) return true
    if (item.children) {
      return item.children.some(child => child.path === location.pathname)
    }
    return false
  }

  const renderMenuItem = (item) => {
    const hasChildren = item.children && item.children.length > 0
    const isExpanded = expandedKeys.includes(item.key)
    const isActive = isMenuActive(item)

    if (hasChildren) {
      return (
        <div key={item.key} className={`menu-item-group ${isActive ? 'active' : ''}`}>
          <div 
            className="menu-item menu-item-parent"
            onClick={() => toggleMenu(item.key)}
          >
            <span className="menu-icon">{item.icon}</span>
            <span className="menu-label">{item.label}</span>
            <span className={`menu-arrow ${isExpanded ? 'expanded' : ''}`}>▶</span>
          </div>
          {isExpanded && (
            <div className="submenu">
              {item.children.map(child => (
                <NavLink
                  key={child.key}
                  to={child.path}
                  className={({ isActive }) => 
                    `submenu-item ${isActive ? 'active' : ''}`
                  }
                >
                  <span className="submenu-icon">{child.icon}</span>
                  <span className="submenu-label">{child.label}</span>
                </NavLink>
              ))}
            </div>
          )}
        </div>
      )
    }

    return (
      <NavLink
        key={item.key}
        to={item.path}
        className={({ isActive }) => 
          `menu-item ${isActive ? 'active' : ''}`
        }
      >
        <span className="menu-icon">{item.icon}</span>
        <span className="menu-label">{item.label}</span>
      </NavLink>
    )
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">🤖</span>
          <span className="logo-text">合肥理财中心</span>
        </div>
        <div className="logo-subtitle">AI辅助系统</div>
      </div>
      
      <nav className="sidebar-menu">
        {menuConfig.map(renderMenuItem)}
      </nav>
      
      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">👤</div>
          <div className="user-details">
            <div className="user-name">客服代表</div>
            <div className="user-role">客户关系部</div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
