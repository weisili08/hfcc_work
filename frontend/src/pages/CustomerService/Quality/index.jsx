import { useState, useEffect } from 'react'
import { analyzeQuality, getQualityRecords } from '../../../services/csApi'
import './Quality.css'

// 模拟质检记录数据
const MOCK_RECORDS = [
  {
    record_id: 'rec_001',
    agent_name: '李小红',
    agent_id: 'agent_001',
    call_date: '2026-04-15',
    duration: 328,
    total_score: 92,
    status: 'completed',
    dimensions: [
      { name: '服务态度', score: 95, weight: 0.3 },
      { name: '业务熟练', score: 90, weight: 0.3 },
      { name: '沟通技巧', score: 93, weight: 0.2 },
      { name: '合规执行', score: 90, weight: 0.2 }
    ],
    issues: [
      { type: '语速过快', severity: 'low', description: '部分时段语速略快' }
    ],
    suggestions: ['建议适当放慢语速', '继续保持良好的服务态度']
  },
  {
    record_id: 'rec_002',
    agent_name: '王小明',
    agent_id: 'agent_002',
    call_date: '2026-04-15',
    duration: 456,
    total_score: 85,
    status: 'completed',
    dimensions: [
      { name: '服务态度', score: 88, weight: 0.3 },
      { name: '业务熟练', score: 82, weight: 0.3 },
      { name: '沟通技巧', score: 86, weight: 0.2 },
      { name: '合规执行', score: 84, weight: 0.2 }
    ],
    issues: [
      { type: '产品介绍不完整', severity: 'medium', description: '未充分说明产品风险' }
    ],
    suggestions: ['加强产品知识培训', '注意风险提示的完整性']
  },
  {
    record_id: 'rec_003',
    agent_name: '张小华',
    agent_id: 'agent_003',
    call_date: '2026-04-14',
    duration: 245,
    total_score: 78,
    status: 'completed',
    dimensions: [
      { name: '服务态度', score: 85, weight: 0.3 },
      { name: '业务熟练', score: 75, weight: 0.3 },
      { name: '沟通技巧', score: 78, weight: 0.2 },
      { name: '合规执行', score: 74, weight: 0.2 }
    ],
    issues: [
      { type: '业务知识不足', severity: 'high', description: '对基金申购流程解释有误' },
      { type: '未确认客户理解', severity: 'medium', description: '重要信息未确认客户已理解' }
    ],
    suggestions: ['加强基金业务培训', '每次重要信息后确认客户理解', '使用标准话术模板']
  },
  {
    record_id: 'rec_004',
    agent_name: '刘小丽',
    agent_id: 'agent_004',
    call_date: '2026-04-14',
    duration: 189,
    total_score: 96,
    status: 'completed',
    dimensions: [
      { name: '服务态度', score: 98, weight: 0.3 },
      { name: '业务熟练', score: 95, weight: 0.3 },
      { name: '沟通技巧', score: 96, weight: 0.2 },
      { name: '合规执行', score: 95, weight: 0.2 }
    ],
    issues: [],
    suggestions: ['表现优秀，可作为标杆案例']
  }
]

// 模拟分析结果
const MOCK_ANALYSIS_RESULT = {
  analysis_id: 'analysis_001',
  status: 'completed',
  transcript: {
    text: '客服：您好，感谢您拨打XX基金客服热线，我是客服专员小李，很高兴为您服务。\n客户：你好，我想咨询一下基金赎回的问题。\n客服：好的，请问您是想了解哪方面的赎回问题呢？\n客户：我昨天提交的赎回申请，为什么今天还没到账？\n客服：非常理解您的着急心情。基金赎回一般需要T+3个工作日到账，您昨天提交的申请，预计会在本周五到账。\n客户：哦，原来是这样，那我再等等。\n客服：好的，如果您还有其他问题，随时可以联系我们。感谢您的来电，祝您生活愉快！',
    segments: []
  },
  score: {
    total: 88,
    dimensions: [
      { name: '服务态度', score: 92, weight: 0.3 },
      { name: '业务熟练', score: 85, weight: 0.3 },
      { name: '沟通技巧', score: 88, weight: 0.2 },
      { name: '合规执行', score: 87, weight: 0.2 }
    ]
  },
  issues: [
    { type: '未主动提供工号', severity: 'low', description: '开场白未主动告知客户工号', timestamp: '00:05' },
    { type: '未确认客户身份', severity: 'medium', description: '未进行客户身份核验' }
  ],
  suggestions: [
    '开场白需包含工号信息',
    '涉及账户操作前需核验客户身份',
    '建议主动提供预计处理时间'
  ],
  is_high_risk: false
}

const statusMap = {
  pending: { label: '待检', color: '#faad14' },
  processing: { label: '分析中', color: '#1890ff' },
  completed: { label: '已完成', color: '#52c41a' },
  failed: { label: '失败', color: '#ff4d4f' }
}

function Quality() {
  const [records, setRecords] = useState(MOCK_RECORDS)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [callText, setCallText] = useState('')
  const [expandedRecord, setExpandedRecord] = useState(null)

  // 统计数据
  const stats = {
    avgScore: Math.round(records.reduce((sum, r) => sum + r.total_score, 0) / records.length),
    pendingCount: records.filter(r => r.status === 'pending').length,
    completedCount: records.filter(r => r.status === 'completed').length
  }

  // 加载质检记录
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getQualityRecords()
        if (res?.data?.items) {
          setRecords(res.data.items)
        }
      } catch (e) {
        console.log('Using mock quality records')
      }
    }
    fetchData()
  }, [])

  const handleAnalyze = async () => {
    if (!callText.trim()) {
      alert('请输入通话文本')
      return
    }

    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const res = await analyzeQuality({
        call_record_id: `call_${Date.now()}`,
        audio_url: '',
        duration: 300,
        agent_id: 'agent_001'
      })

      if (res?.data) {
        setAnalysisResult(res.data)
      }
    } catch (e) {
      console.log('Using mock analysis result')
      setTimeout(() => {
        setAnalysisResult({
          ...MOCK_ANALYSIS_RESULT,
          transcript: { ...MOCK_ANALYSIS_RESULT.transcript, text: callText }
        })
      }, 2000)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 90) return '#52c41a'
    if (score >= 80) return '#1890ff'
    if (score >= 70) return '#faad14'
    return '#ff4d4f'
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}分${secs}秒`
  }

  // 雷达图数据计算
  const renderRadarChart = (dimensions) => {
    const size = 200
    const center = size / 2
    const radius = 80
    const angleStep = (Math.PI * 2) / dimensions.length

    // 计算各点坐标
    const points = dimensions.map((dim, i) => {
      const angle = i * angleStep - Math.PI / 2
      const r = (dim.score / 100) * radius
      return {
        x: center + r * Math.cos(angle),
        y: center + r * Math.sin(angle),
        label: dim.name,
        score: dim.score
      }
    })

    // 网格线
    const gridLines = [20, 40, 60, 80, 100].map(level => {
      const r = (level / 100) * radius
      const gridPoints = dimensions.map((_, i) => {
        const angle = i * angleStep - Math.PI / 2
        return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`
      }).join(' ')
      return (
        <polygon
          key={level}
          points={gridPoints}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="1"
        />
      )
    })

    // 轴线
    const axes = dimensions.map((_, i) => {
      const angle = i * angleStep - Math.PI / 2
      const x2 = center + radius * Math.cos(angle)
      const y2 = center + radius * Math.sin(angle)
      return (
        <line
          key={i}
          x1={center}
          y1={center}
          x2={x2}
          y2={y2}
          stroke="#e2e8f0"
          strokeWidth="1"
        />
      )
    })

    // 数据区域
    const dataPoints = points.map(p => `${p.x},${p.y}`).join(' ')

    // 标签
    const labels = points.map((p, i) => {
      const angle = i * angleStep - Math.PI / 2
      const labelR = radius + 20
      const x = center + labelR * Math.cos(angle)
      const y = center + labelR * Math.sin(angle)
      return (
        <text
          key={i}
          x={x}
          y={y}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="12"
          fill="#4a5568"
        >
          {p.label}
        </text>
      )
    })

    // 分数标签
    const scoreLabels = points.map((p, i) => (
      <text
        key={`score-${i}`}
        x={p.x}
        y={p.y - 8}
        textAnchor="middle"
        fontSize="10"
        fill="#1a365d"
        fontWeight="600"
      >
        {p.score}
      </text>
    ))

    return (
      <svg width={size} height={size} className="radar-chart">
        {gridLines}
        {axes}
        <polygon
          points={dataPoints}
          fill="rgba(74, 144, 217, 0.2)"
          stroke="#4a90d9"
          strokeWidth="2"
        />
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="4"
            fill="#4a90d9"
          />
        ))}
        {labels}
        {scoreLabels}
      </svg>
    )
  }

  return (
    <div className="quality-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">质检管理</h1>
        <p className="page-subtitle">通话录音质检分析、多维度评分、改进建议</p>
      </div>

      {/* 统计卡片 */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(24, 144, 255, 0.1)', color: '#1890ff' }}>
            📊
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.avgScore}</div>
            <div className="stat-label">平均分</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(250, 173, 20, 0.1)', color: '#faad14' }}>
            ⏳
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.pendingCount}</div>
            <div className="stat-label">待检数</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(82, 196, 26, 0.1)', color: '#52c41a' }}>
            ✅
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.completedCount}</div>
            <div className="stat-label">已完成</div>
          </div>
        </div>
      </div>

      <div className="quality-content">
        {/* 左侧：AI分析区 */}
        <div className="analysis-section">
          <div className="section-card">
            <h3 className="section-title">🤖 AI质检分析</h3>
            <div className="analysis-input">
              <label>输入通话文本</label>
              <textarea
                rows={8}
                value={callText}
                onChange={(e) => setCallText(e.target.value)}
                placeholder="请粘贴通话录音转录文本，AI将自动分析质检评分..."
              />
              <button
                className="analyze-btn"
                onClick={handleAnalyze}
                disabled={isAnalyzing || !callText.trim()}
              >
                {isAnalyzing ? (
                  <>
                    <span className="spinner"></span>
                    AI分析中...
                  </>
                ) : (
                  <>
                    <span>🔍</span> AI分析
                  </>
                )}
              </button>
            </div>
          </div>

          {/* 分析结果 */}
          {analysisResult && (
            <div className="section-card analysis-result">
              <div className="result-header">
                <h4>分析结果</h4>
                <span 
                  className="total-score"
                  style={{ color: getScoreColor(analysisResult.score.total) }}
                >
                  {analysisResult.score.total}分
                </span>
              </div>

              {/* 雷达图 */}
              <div className="radar-chart-container">
                {renderRadarChart(analysisResult.score.dimensions)}
              </div>

              {/* 维度分数 */}
              <div className="dimension-scores">
                {analysisResult.score.dimensions.map((dim, idx) => (
                  <div key={idx} className="dimension-item">
                    <span className="dim-name">{dim.name}</span>
                    <div className="dim-bar">
                      <div 
                        className="dim-fill"
                        style={{ 
                          width: `${dim.score}%`,
                          backgroundColor: getScoreColor(dim.score)
                        }}
                      />
                    </div>
                    <span 
                      className="dim-score"
                      style={{ color: getScoreColor(dim.score) }}
                    >
                      {dim.score}
                    </span>
                  </div>
                ))}
              </div>

              {/* 问题点 */}
              {analysisResult.issues.length > 0 && (
                <div className="issues-section">
                  <h5>⚠️ 问题点</h5>
                  <ul>
                    {analysisResult.issues.map((issue, idx) => (
                      <li key={idx} className={`issue-${issue.severity}`}>
                        <span className="issue-type">{issue.type}</span>
                        <span className="issue-desc">{issue.description}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 改进建议 */}
              <div className="suggestions-section">
                <h5>💡 改进建议</h5>
                <ul>
                  {analysisResult.suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* 右侧：质检记录表 */}
        <div className="records-section">
          <div className="section-card">
            <h3 className="section-title">质检记录</h3>
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
                    <th>客服姓名</th>
                    <th>日期</th>
                    <th>时长</th>
                    <th>得分</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((record, index) => (
                    <>
                      <tr
                        key={record.record_id}
                        className={`${index % 2 === 1 ? 'even' : ''} ${expandedRecord === record.record_id ? 'expanded' : ''}`}
                        onClick={() => setExpandedRecord(expandedRecord === record.record_id ? null : record.record_id)}
                      >
                        <td>{record.agent_name}</td>
                        <td>{record.call_date}</td>
                        <td>{formatDuration(record.duration)}</td>
                        <td>
                          <span 
                            className="score-badge"
                            style={{ color: getScoreColor(record.total_score) }}
                          >
                            {record.total_score}
                          </span>
                        </td>
                        <td>
                          <span 
                            className="status-badge"
                            style={{ color: statusMap[record.status]?.color }}
                          >
                            {statusMap[record.status]?.label}
                          </span>
                        </td>
                      </tr>
                      {expandedRecord === record.record_id && (
                        <tr className="detail-row">
                          <td colSpan={5}>
                            <div className="record-detail">
                              <div className="detail-radar">
                                {renderRadarChart(record.dimensions)}
                              </div>
                              <div className="detail-info">
                                <h5>各维度得分</h5>
                                <div className="detail-dimensions">
                                  {record.dimensions.map((dim, idx) => (
                                    <div key={idx} className="detail-dim-item">
                                      <span>{dim.name}</span>
                                      <span style={{ color: getScoreColor(dim.score) }}>
                                        {dim.score}分
                                      </span>
                                    </div>
                                  ))}
                                </div>
                                {record.issues.length > 0 && (
                                  <div className="detail-issues">
                                    <h5>问题点</h5>
                                    <ul>
                                      {record.issues.map((issue, idx) => (
                                        <li key={idx}>{issue.type}: {issue.description}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Quality
