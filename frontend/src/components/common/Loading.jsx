import './Loading.css'

function Loading({ fullScreen = false, size = 'medium', text = '加载中...' }) {
  const sizeMap = {
    small: 'loading-spinner-small',
    medium: 'loading-spinner-medium',
    large: 'loading-spinner-large'
  }

  const spinnerClass = sizeMap[size] || sizeMap.medium

  if (fullScreen) {
    return (
      <div className="loading-fullscreen">
        <div className="loading-content">
          <div className={`loading-spinner ${spinnerClass}`} />
          <span className="loading-text">{text}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="loading-inline">
      <div className={`loading-spinner ${spinnerClass}`} />
      <span className="loading-text">{text}</span>
    </div>
  )
}

export default Loading
