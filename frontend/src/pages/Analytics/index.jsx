import { useState, useEffect } from 'react'
import { analyzePortrait, detectAnomaly, generateReport, getChurnRisk } from '../../services/analyticsApi'
import './Analytics.css'

// Tab配置
const TABS = [
  { key: 'portrait', label: '客户画像', icon: '👤' },
  { key: 'anomaly', label: '异常监控', icon: '⚠️' },
  { key: 'churn', label: '流失预警', icon: '📉' },
  { key: 'reports', label: '报表中心', icon: '📊' }
]

// 模拟客户画像数据
const MOCK_PORTRAIT = {
  analysis_id: 'portrait_001',
  total_customers: 12580,
  portrait_summary: {
    demographics: {
      age_distribution: { '20-30': 15, '30-40': 35, '40-50': 30, '50-60': 15, '60+': 5 },
      gender_distribution: { male: 52, female: 48 }
    },
    holding_distribution: {
      '10万以下': 25,
      '10-50万': 35,
      '50-100万': 22,
      '100-500万': 14,
      '500万以上': 4
    },
    risk_profile: {
      'C1-保守型': 12,
      'C2-稳健型': 28,
      'C3-平衡型': 35,
      'C4-成长型': 18,
      'C5-进取型': 7
    }
  },
  segments: [
    { segment_id: 'seg_001', segment_name: '高净值稳健型', customer_count: 2156, characteristics: { avg_aum: 280, main_products: ['债券基金', '货币基金'] } },
    { segment_id: 'seg_002', segment_name: '年轻成长型', customer_count: 4521, characteristics: { avg_aum: 45, main_products: ['股票基金', '混合基金'] } },
    { segment_id: 'seg_003', segment_name: '退休保守型', customer_count: 1890, characteristics: { avg_aum: 120, main_products: ['货币基金', '定期理财'] } }
  ],
  tag_distribution: {
    '活跃交易': 3250,
    '长期持有': 4890,
    '定投用户': 2100,
    '高净值': 1560,
    '新客': 780
  }
}

// 模拟异常数据
const MOCK_ANOMALIES = [
  {
    alert_id: 'ALT001',
    customer_id: 'CUST****1234',
    customer_name: '张**',
    anomaly_type: 'large_redemption',
    anomaly_type_desc: '大额赎回预警',
    detected_at: '2026-04-16T10:30:00Z',
    amount: 500000,
    risk_level: 'high',
    description: '客户单日赎回金额超过50万，超过历史平均水平的10倍',
    suggested_action: '立即联系客户了解赎回原因，提供替代方案',
    status: 'new'
  },
  {
    alert_id: 'ALT002',
    customer_id: 'CUST****5678',
    customer_name: '李**',
    anomaly_type: 'frequent_trading',
    anomaly_type_desc: '频繁交易异常',
    detected_at: '2026-04-16T09:15:00Z',
    amount: 120000,
    risk_level: 'medium',
    description: '客户本周交易次数超过20次，疑似异常操作',
    suggested_action: '关注客户交易行为，必要时进行风险提示',
    status: 'processing'
  },
  {
    alert_id: 'ALT003',
    customer_id: 'CUST****9012',
    customer_name: '王**',
    anomaly_type: 'login_anomaly',
    anomaly_type_desc: '登录异常',
    detected_at: '2026-04-15T22:45:00Z',
    amount: 0,
    risk_level: 'high',
    description: '客户账户在非常用地点登录，且登录时间异常',
    suggested_action: '立即冻结账户并联系客户确认',
    status: 'resolved'
  }
]

// 模拟流失预警数据
const MOCK_CHURN_RISKS = [
  {
    customer_id: 'CUST****1111',
    customer_name: '赵**',
    risk_score: 85,
    risk_level: 'high',
    risk_factors: [
      { factor: '持仓收益持续为负', weight: 0.4 },
      { factor: '近30天无登录', weight: 0.3 },
      { factor: '客服投诉记录', weight: 0.3 }
    ],
    predicted_churn_date: '2026-05-15',
    intervention_suggestions: ['主动回访了解投资困扰', '提供组合优化建议', '赠送费率优惠券']
  },
  {
    customer_id: 'CUST****2222',
    customer_name: '钱**',
    risk_score: 72,
    risk_level: 'medium',
    risk_factors: [
      { factor: '赎回频率增加', weight: 0.5 },
      { factor: '持仓比例下降', weight: 0.5 }
    ],
    predicted_churn_date: '2026-06-01',
    intervention_suggestions: ['分析赎回原因', '推荐更适合的产品']
  },
  {
    customer_id: 'CUST****3333',
    customer_name: '孙**',
    risk_score: 68,
    risk_level: 'medium',
    risk_factors: [
      { factor: '客服满意度低', weight: 0.6 },
      { factor: '产品咨询减少', weight: 0.4 }
    ],
    predicted_churn_date: '2026-05-20',
    intervention_suggestions: ['提升服务质量', '定期关怀回访']
  }
]

// 模拟报表数据
const MOCK_REPORTS = [
  { report_id: 'rpt_001', report_type: 'daily', title: '日报-20260416', created_at: '2026-04-16T08:00:00Z', status: 'completed' },
  { report_id: 'rpt_002', report_type: 'weekly', title: '周报-2026W16', created_at: '2026-04-14T18:00:00Z', status: 'completed' },
  { report_id: 'rpt_003', report_type: 'monthly', title: '月报-2026年4月', created_at: '2026-04-01T10:00:00Z', status: 'completed' }
]

const riskLevelMap = {
  high: { label: '高风险', color: '#ff4d4f' },
  medium: { label: '中风险', color: '#faad14' },
  low: { label: '低风险', color: '#52c41a' }
}

const anomalyTypeMap = {
  large_redemption: '大额赎回',
  frequent_trading: '频繁交易',
  login_anomaly: '登录异常'
}

function Analytics() {
  const [activeTab, setActiveTab] = useState('portrait')
  const [portraitData, setPortraitData] = useState(MOCK_PORTRAIT)
  const [anomalies, setAnomalies] = useState(MOCK_ANOMALIES)
  const [churnRisks, setChurnRisks] = useState(MOCK_CHURN_RISKS)
  const [reports, setReports] = useState(MOCK_REPORTS)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [generatedReport, setGeneratedReport] = useState(null)
  const [selectedCustomerForPortrait, setSelectedCustomerForPortrait] = useState('')

  // 加载数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 可以在这里并行加载多个API
      } catch (e) {
        console.log('Using mock data')
      }
    }
    fetchData()
  }, [])

  // 生成AI客户画像分析
  const handleAnalyzePortrait = async () => {
    try {
      const res = await analyzePortrait({
        customer_ids: selectedCustomerForPortrait ? [selectedCustomerForPortrait] : [],
        analysis_scope: selectedCustomerForPortrait ? 'selected' : 'all'
      })
      if (res?.data) {
        setPortraitData(res.data)
      }
    } catch (e) {
      console.log('Using mock portrait data')
    }
  }

  // 生成AI报表
  const handleGenerateReport = async () => {
    setIsGeneratingReport(true)
    try {
      const res = await generateReport({
        report_type: 'custom',
        sections: ['overview', 'trends', 'recommendations']
      })
      if (res?.data) {
        setGeneratedReport(res.data)
      }
    } catch (e) {
      console.log('Using mock report')
      setTimeout(() => {
        setGeneratedReport({
          report_id: 'rpt_new_001',
          report_type: 'custom',
          generated_at: new Date().toISOString(),
          summary: {
            ai_summary: '本周期客户活跃度整体提升15%，高净值客户留存率达到92%。需关注近期市场波动对中低风险客户的影响。',
            key_findings: [
              '新客户转化率提升8个百分点',
              '基金定投用户增长23%',
              '客户满意度评分4.6/5.0'
            ]
          }
        })
      }, 1500)
    } finally {
      setIsGeneratingReport(false)
    }
  }

  // 渲染客户画像Tab
  const renderPortraitTab = () => (
    <div className="tab-content">
      <div className="portrait-panel">
        <div className="panel-header">
          <h3>客户画像分析</h3>
          <div className="header-actions">
            <input
              type="text"
              placeholder="输入客户号（可选）"
              value={selectedCustomerForPortrait}
              onChange={(e) => setSelectedCustomerForPortrait(e.target.value)}
              className="customer-input"
            />
            <button className="analyze-btn" onClick={handleAnalyzePortrait}>
              🤖 AI分析画像
            </button>
          </div>
        </div>

        <div className="portrait-stats">
          <div className="stat-card large">
            <span className="stat-number">{portraitData.total_customers.toLocaleString()}</span>
            <span className="stat-label">分析客户总数</span>
          </div>
        </div>

        <div className="portrait-grids">
          {/* 年龄分布 */}
          <div className="portrait-card">
            <h4>年龄分布</h4>
            <div className="distribution-bars">
              {Object.entries(portraitData.portrait_summary.demographics.age_distribution).map(([age, pct]) => (
                <div key={age} className="dist-bar-item">
                  <span className="dist-label">{age}岁</span>
                  <div className="dist-bar">
                    <div className="dist-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="dist-value">{pct}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* 持仓分布 */}
          <div className="portrait-card">
            <h4>持仓金额分布</h4>
            <div className="distribution-bars">
              {Object.entries(portraitData.portrait_summary.holding_distribution).map(([range, pct]) => (
                <div key={range} className="dist-bar-item">
                  <span className="dist-label">{range}</span>
                  <div className="dist-bar">
                    <div className="dist-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="dist-value">{pct}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* 风险偏好 */}
          <div className="portrait-card">
            <h4>风险偏好分布</h4>
            <div className="risk-distribution">
              {Object.entries(portraitData.portrait_summary.risk_profile).map(([risk, pct]) => (
                <div key={risk} className="risk-item">
                  <span className="risk-name">{risk}</span>
                  <div className="risk-bar">
                    <div className="risk-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="risk-value">{pct}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* 客户分群 */}
          <div className="portrait-card wide">
            <h4>客户分群</h4>
            <div className="segments-list">
              {portraitData.segments.map(segment => (
                <div key={segment.segment_id} className="segment-card">
                  <div className="segment-header">
                    <h5>{segment.segment_name}</h5>
                    <span className="segment-count">{segment.customer_count.toLocaleString()}人</span>
                  </div>
                  <div className="segment-stats">
                    <span>人均AUM: {segment.characteristics.avg_aum}万</span>
                    <span>偏好: {segment.characteristics.main_products.join('、')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 标签云 */}
          <div className="portrait-card wide">
            <h4>客户标签分布</h4>
            <div className="tag-cloud">
              {Object.entries(portraitData.tag_distribution).map(([tag, count]) => (
                <span key={tag} className="tag-item" style={{ fontSize: `${0.8 + count / 5000}rem` }}>
                  {tag} ({count})
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  // 渲染异常监控Tab
  const renderAnomalyTab = () => (
    <div className="tab-content">
      <div className="anomaly-panel">
        <div className="panel-header">
          <h3>异常监控告警</h3>
          <div className="alert-stats">
            <span className="alert-stat high">高风险: {anomalies.filter(a => a.risk_level === 'high').length}</span>
            <span className="alert-stat medium">中风险: {anomalies.filter(a => a.risk_level === 'medium').length}</span>
          </div>
        </div>

        <div className="alerts-list">
          {anomalies.map(alert => (
            <div key={alert.alert_id} className={`alert-card ${alert.risk_level}`}>
              <div className="alert-header">
                <div className="alert-type">
                  <span className="type-icon">⚠️</span>
                  <span className="type-name">{anomalyTypeMap[alert.anomaly_type]}</span>
                </div>
                <span 
                  className="risk-badge"
                  style={{ color: riskLevelMap[alert.risk_level].color }}
                >
                  {riskLevelMap[alert.risk_level].label}
                </span>
              </div>
              <div className="alert-body">
                <p className="alert-desc">{alert.description}</p>
                <div className="alert-meta">
                  <span>客户: {alert.customer_name}</span>
                  {alert.amount > 0 && <span>金额: ¥{alert.amount.toLocaleString()}</span>}
                  <span>时间: {new Date(alert.detected_at).toLocaleString('zh-CN')}</span>
                </div>
              </div>
              <div className="alert-footer">
                <div className="suggested-action">
                  <strong>建议措施:</strong> {alert.suggested_action}
                </div>
                <div className="alert-actions">
                  <button className="action-btn">处理</button>
                  <button className="action-btn secondary">忽略</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  // 渲染流失预警Tab
  const renderChurnTab = () => (
    <div className="tab-content">
      <div className="churn-panel">
        <div className="panel-header">
          <h3>流失风险预警</h3>
          <div className="churn-stats">
            <span className="churn-stat high">高风险: {churnRisks.filter(c => c.risk_level === 'high').length}</span>
            <span className="churn-stat medium">中风险: {churnRisks.filter(c => c.risk_level === 'medium').length}</span>
          </div>
        </div>

        <div className="churn-list">
          {churnRisks.map(customer => (
            <div key={customer.customer_id} className={`churn-card ${customer.risk_level}`}>
              <div className="churn-header">
                <div className="customer-info">
                  <h4>{customer.customer_name}</h4>
                  <span className="customer-id">{customer.customer_id}</span>
                </div>
                <div className="risk-score">
                  <div className="score-circle" style={{ 
                    background: `conic-gradient(${riskLevelMap[customer.risk_level].color} ${customer.risk_score}%, #e2e8f0 0)` 
                  }}>
                    <span>{customer.risk_score}</span>
                  </div>
                  <span className="risk-label">{riskLevelMap[customer.risk_level].label}</span>
                </div>
              </div>
              
              <div className="risk-factors">
                <h5>风险因子</h5>
                {customer.risk_factors.map((factor, idx) => (
                  <div key={idx} className="factor-item">
                    <span className="factor-name">{factor.factor}</span>
                    <div className="factor-bar">
                      <div className="factor-fill" style={{ width: `${factor.weight * 100}%` }} />
                    </div>
                    <span className="factor-weight">{Math.round(factor.weight * 100)}%</span>
                  </div>
                ))}
              </div>

              <div className="predicted-date">
                <span>预计流失时间: {customer.predicted_churn_date}</span>
              </div>

              <div className="intervention-suggestions">
                <h5>挽留建议</h5>
                <ul>
                  {customer.intervention_suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>

              <div className="churn-actions">
                <button className="action-btn primary">生成挽留方案</button>
                <button className="action-btn">标记已处理</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  // 渲染报表中心Tab
  const renderReportsTab = () => (
    <div className="tab-content">
      <div className="reports-panel">
        <div className="panel-header">
          <h3>报表中心</h3>
          <button 
            className="generate-btn"
            onClick={handleGenerateReport}
            disabled={isGeneratingReport}
          >
            {isGeneratingReport ? 'AI生成中...' : '✨ AI生成报表'}
          </button>
        </div>

        {generatedReport && (
          <div className="generated-report">
            <h4>🤖 AI生成报表</h4>
            <div className="report-summary">
              <h5>AI摘要</h5>
              <p>{generatedReport.summary.ai_summary}</p>
            </div>
            <div className="key-findings">
              <h5>关键发现</h5>
              <ul>
                {generatedReport.summary.key_findings.map((finding, idx) => (
                  <li key={idx}>{finding}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        <div className="reports-list">
          <h4>历史报表</h4>
          {reports.map(report => (
            <div key={report.report_id} className="report-card">
              <div className="report-icon">📄</div>
              <div className="report-info">
                <h5>{report.title}</h5>
                <span className="report-type">{report.report_type === 'daily' ? '日报' : report.report_type === 'weekly' ? '周报' : '月报'}</span>
              </div>
              <div className="report-meta">
                <span>{new Date(report.created_at).toLocaleDateString('zh-CN')}</span>
                <span className="status-badge">{report.status === 'completed' ? '已完成' : '生成中'}</span>
              </div>
              <button className="download-btn">下载</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="analytics-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">数据分析与洞察</h1>
        <p className="page-subtitle">画像分析引擎、异常检测引擎、报表生成引擎、流失预测引擎</p>
      </div>

      {/* Tab导航 */}
      <div className="tab-nav">
        {TABS.map(tab => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab内容 */}
      {activeTab === 'portrait' && renderPortraitTab()}
      {activeTab === 'anomaly' && renderAnomalyTab()}
      {activeTab === 'churn' && renderChurnTab()}
      {activeTab === 'reports' && renderReportsTab()}
    </div>
  )
}

export default Analytics
