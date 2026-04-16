import { Link } from 'react-router-dom'
import './NotFound.css'

function NotFound() {
  return (
    <div className="not-found">
      <div className="not-found-content">
        <div className="not-found-icon">🔍</div>
        <h1 className="not-found-title">404</h1>
        <h2 className="not-found-subtitle">页面未找到</h2>
        <p className="not-found-description">
          抱歉，您访问的页面不存在或已被移除。
        </p>
        <div className="not-found-actions">
          <Link to="/" className="btn btn-primary">
            返回主控台
          </Link>
          <button 
            className="btn btn-secondary"
            onClick={() => window.history.back()}
          >
            返回上一页
          </button>
        </div>
      </div>
    </div>
  )
}

export default NotFound
