import { useState, useEffect } from 'react'
import { getSentiment, analyzeCompetitor, getMarketTrends } from '../../services/marketApi'
import './Market.css'

// Tab配置
const TABS = [
  { key: 'sentiment', label: '舆情监控', icon: '👁️' },
  { key: 'products', label: '产品研究', icon: '🔬' },
  { key: 'trends', label: '市场动态', icon: '📈' }
]

// 模拟舆情数据
const MOCK_SENTIMENTS = [
  {
    mention_id: 'men_001',
    source: '财经新闻',
    source_type: 'news',
    published_at: '2026-04-16T10:30:00Z',
    title: '公募基金一季度业绩回顾',
    content_snippet: '今年一季度，权益类基金整体表现良好，平均收益率达到8.5%，其中科技主题基金表现突出...',
    sentiment: 'positive',
    sentiment_score: 0.75,
    related_products: ['XX科技主题基金', 'YY成长混合']
  },
  {
    mention_id: 'men_002',
    source: '投资者论坛',
    source_type: 'forum',
    published_at: '2026-04-16T09:15:00Z',
    title: '关于最近债券基金下跌的讨论',
    content_snippet: '最近债市波动较大，持有的债券基金连续下跌，是否应该赎回？',
    sentiment: 'negative',
    sentiment_score: -0.45,
    related_products: ['XX债券基金', 'YY纯债基金']
  },
  {
    mention_id: 'men_003',
    source: '社交媒体',
    source_type: 'social',
    published_at: '2026-04-15T16:45:00Z',
    title: '定投三年的心得分享',
    content_snippet: '坚持定投三年了，虽然中间有波动，但整体收益还不错，建议大家保持耐心...',
    sentiment: 'positive',
    sentiment_score: 0.62,
    related_products: ['定投计划', '指数基金']
  },
  {
    mention_id: 'men_004',
    source: '新闻报道',
    source_type: 'news',
    published_at: '2026-04-15T14:20:00Z',
    title: '央行发布最新货币政策',
    content_snippet: '央行今日宣布维持基准利率不变，市场流动性保持合理充裕...',
    sentiment: 'neutral',
    sentiment_score: 0.05,
    related_products: ['货币基金', '债券基金']
  }
]

// 模拟竞品分析数据
const MOCK_COMPETITOR_ANALYSIS = {
  analysis_id: 'comp_001',
  comparison_matrix: {
    products: ['XX稳健增长', 'YY价值精选', 'ZZ成长先锋'],
    dimensions: ['近一年收益', '最大回撤', '夏普比率', '管理费率'],
    data: {
      'XX稳健增长': { return: 12.5, drawdown: -8.2, sharpe: 1.35, fee: 1.5 },
      'YY价值精选': { return: 15.8, drawdown: -12.5, sharpe: 1.18, fee: 1.2 },
      'ZZ成长先锋': { return: 22.3, drawdown: -18.6, sharpe: 1.05, fee: 1.5 }
    }
  },
  ai_analysis: {
    summary: '三款产品各有特色，XX稳健增长风险控制好，YY价值精选性价比较高，ZZ成长先锋收益潜力大但波动也大。',
    competitive_advantages: ['费率相对较低', '风险控制能力较强', '长期业绩稳定'],
    competitive_disadvantages: ['短期爆发力不足', '规模偏大影响灵活性'],
    differentiation: '建议主打稳健增值定位，强调风险控制能力和长期复利效应。',
    market_positioning: '中等风险中等收益产品，适合追求稳健增值的投资者。'
  }
}

// 模拟市场动态数据
const MOCK_TRENDS = [
  {
    trend_id: 'trend_001',
    category: 'policy',
    title: '新《证券法》实施细则发布',
    description: '证监会发布新《证券法》实施细则，对公募基金信息披露提出更高要求',
    impact_level: 'high',
    occurred_at: '2026-04-16T08:00:00Z',
    related_products: ['全市场基金'],
    impact_analysis: '短期内可能增加合规成本，长期有利于行业规范发展',
    suggested_response: '加强合规培训，完善信息披露流程'
  },
  {
    trend_id: 'trend_002',
    category: 'market',
    title: '科技股板块持续走强',
    description: '受AI概念带动，科技股板块近期表现活跃',
    impact_level: 'medium',
    occurred_at: '2026-04-15T15:30:00Z',
    related_products: ['科技主题基金', '成长型基金'],
    impact_analysis: '科技主题基金净值上涨，投资者关注度提升',
    suggested_response: '关注估值风险，适时提示投资者'
  },
  {
    trend_id: 'trend_003',
    category: 'industry',
    title: '银行理财子公司新规出台',
    description: '银保监会发布银行理财子公司管理办法修订稿',
    impact_level: 'medium',
    occurred_at: '2026-04-14T10:00:00Z',
    related_products: ['混合型基金'],
    impact_analysis: '银行理财与公募基金竞争加剧',
    suggested_response: '强化产品差异化优势'
  }
]

const sentimentMap = {
  positive: { label: '正面', color: '#52c41a', bg: '#f6ffed' },
  neutral: { label: '中性', color: '#8c8c8c', bg: '#f5f5f5' },
  negative: { label: '负面', color: '#ff4d4f', bg: '#fff1f0' }
}

const categoryMap = {
  policy: { label: '政策', color: '#1890ff' },
  market: { label: '市场', color: '#52c41a' },
  industry: { label: '行业', color: '#722ed1' },
  fund: { label: '基金', color: '#faad14' }
}

const impactMap = {
  high: { label: '高影响', color: '#ff4d4f' },
  medium: { label: '中影响', color: '#faad14' },
  low: { label: '低影响', color: '#52c41a' }
}

function Market() {
  const [activeTab, setActiveTab] = useState('sentiment')
  const [sentiments, setSentiments] = useState(MOCK_SENTIMENTS)
  const [competitorAnalysis, setCompetitorAnalysis] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [trends, setTrends] = useState(MOCK_TRENDS)
  const [sentimentFilter, setSentimentFilter] = useState('')

  // 统计数据
  const sentimentStats = {
    total: sentiments.length,
    positive: sentiments.filter(s => s.sentiment === 'positive').length,
    neutral: sentiments.filter(s => s.sentiment === 'neutral').length,
    negative: sentiments.filter(s => s.sentiment === 'negative').length
  }

  // 加载数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getSentiment()
        if (res?.data?.mentions) {
          setSentiments(res.data.mentions)
        }
      } catch (e) {
        console.log('Using mock sentiment data')
      }
    }
    fetchData()
  }, [])

  // 竞品分析
  const handleAnalyzeCompetitor = async () => {
    setIsAnalyzing(true)
    try {
      const res = await analyzeCompetitor({
        product_codes: ['prod_001', 'prod_002', 'prod_003'],
        comparison_dimensions: ['return', 'risk', 'fee']
      })
      if (res?.data) {
        setCompetitorAnalysis(res.data)
      }
    } catch (e) {
      console.log('Using mock competitor analysis')
      setTimeout(() => {
        setCompetitorAnalysis(MOCK_COMPETITOR_ANALYSIS)
      }, 1500)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // 渲染舆情监控Tab
  const renderSentimentTab = () => (
    <div className="tab-content">
      {/* 舆情统计 */}
      <div className="sentiment-stats">
        <div className="stat-card">
          <span className="stat-value">{sentimentStats.total}</span>
          <span className="stat-label">总提及</span>
        </div>
        <div className="stat-card positive">
          <span className="stat-value">{sentimentStats.positive}</span>
          <span className="stat-label">正面</span>
        </div>
        <div className="stat-card neutral">
          <span className="stat-value">{sentimentStats.neutral}</span>
          <span className="stat-label">中性</span>
        </div>
        <div className="stat-card negative">
          <span className="stat-value">{sentimentStats.negative}</span>
          <span className="stat-label">负面</span>
        </div>
      </div>

      {/* 筛选和列表 */}
      <div className="sentiment-panel">
        <div className="panel-header">
          <h3>舆情列表</h3>
          <select 
            className="filter-select"
            value={sentimentFilter}
            onChange={(e) => setSentimentFilter(e.target.value)}
          >
            <option value="">全部情感</option>
            <option value="positive">正面</option>
            <option value="neutral">中性</option>
            <option value="negative">负面</option>
          </select>
        </div>

        <div className="sentiment-list">
          {sentiments
            .filter(s => !sentimentFilter || s.sentiment === sentimentFilter)
            .map(item => (
            <div key={item.mention_id} className="sentiment-card">
              <div className="sentiment-header">
                <div className="source-info">
                  <span className="source-name">{item.source}</span>
                  <span className="publish-time">
                    {new Date(item.published_at).toLocaleString('zh-CN')}
                  </span>
                </div>
                <span 
                  className="sentiment-badge"
                  style={{ 
                    backgroundColor: sentimentMap[item.sentiment].bg,
                    color: sentimentMap[item.sentiment].color 
                  }}
                >
                  {sentimentMap[item.sentiment].label}
                </span>
              </div>
              <h4 className="sentiment-title">{item.title}</h4>
              <p className="sentiment-content">{item.content_snippet}</p>
              <div className="sentiment-footer">
                <div className="related-products">
                  {item.related_products.map((product, idx) => (
                    <span key={idx} className="product-tag">{product}</span>
                  ))}
                </div>
                <span className="sentiment-score">
                  情感得分: {item.sentiment_score > 0 ? '+' : ''}{item.sentiment_score}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  // 渲染产品研究Tab
  const renderProductsTab = () => (
    <div className="tab-content">
      <div className="products-panel">
        <div className="panel-header">
          <h3>产品竞品分析</h3>
          <button 
            className="analyze-btn"
            onClick={handleAnalyzeCompetitor}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? 'AI分析中...' : '🔬 AI产品分析'}
          </button>
        </div>

        {competitorAnalysis && (
          <div className="analysis-result">
            {/* 对比表格 */}
            <div className="comparison-table">
              <h4>竞品对比</h4>
              <table>
                <thead>
                  <tr>
                    <th>产品</th>
                    <th>近一年收益</th>
                    <th>最大回撤</th>
                    <th>夏普比率</th>
                    <th>管理费率</th>
                  </tr>
                </thead>
                <tbody>
                  {competitorAnalysis.comparison_matrix.products.map((product, idx) => {
                    const data = competitorAnalysis.comparison_matrix.data[product]
                    return (
                      <tr key={idx}>
                        <td className="product-name">{product}</td>
                        <td className="positive">+{data.return}%</td>
                        <td className="negative">{data.drawdown}%</td>
                        <td>{data.sharpe}</td>
                        <td>{data.fee}%</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* AI分析结果 */}
            <div className="ai-analysis">
              <h4>🤖 AI分析结论</h4>
              <div className="analysis-section">
                <p className="summary">{competitorAnalysis.ai_analysis.summary}</p>
              </div>
              
              <div className="analysis-grid">
                <div className="analysis-card advantages">
                  <h5>竞争优势</h5>
                  <ul>
                    {competitorAnalysis.ai_analysis.competitive_advantages.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div className="analysis-card disadvantages">
                  <h5>竞争劣势</h5>
                  <ul>
                    {competitorAnalysis.ai_analysis.competitive_disadvantages.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="analysis-section">
                <h5>差异化建议</h5>
                <p>{competitorAnalysis.ai_analysis.differentiation}</p>
              </div>

              <div className="analysis-section">
                <h5>市场定位</h5>
                <p>{competitorAnalysis.ai_analysis.market_positioning}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  // 渲染市场动态Tab
  const renderTrendsTab = () => (
    <div className="tab-content">
      <div className="trends-panel">
        <h3>市场动态信息流</h3>
        <div className="trends-timeline">
          {trends.map(trend => (
            <div key={trend.trend_id} className="trend-item">
              <div className="trend-marker">
                <span 
                  className="category-dot"
                  style={{ backgroundColor: categoryMap[trend.category]?.color }}
                />
                <span className="trend-time">
                  {new Date(trend.occurred_at).toLocaleDateString('zh-CN')}
                </span>
              </div>
              <div className="trend-card">
                <div className="trend-header">
                  <span 
                    className="category-badge"
                    style={{ color: categoryMap[trend.category]?.color }}
                  >
                    {categoryMap[trend.category]?.label}
                  </span>
                  <span 
                    className="impact-badge"
                    style={{ color: impactMap[trend.impact_level]?.color }}
                  >
                    {impactMap[trend.impact_level]?.label}
                  </span>
                </div>
                <h4>{trend.title}</h4>
                <p>{trend.description}</p>
                
                <div className="trend-analysis">
                  <div className="analysis-section">
                    <label>影响分析</label>
                    <p>{trend.impact_analysis}</p>
                  </div>
                  <div className="analysis-section">
                    <label>应对建议</label>
                    <p>{trend.suggested_response}</p>
                  </div>
                </div>

                <div className="related-products">
                  {trend.related_products.map((product, idx) => (
                    <span key={idx} className="product-tag">{product}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="market-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">市场监测</h1>
        <p className="page-subtitle">舆情采集、竞品分析、市场动态</p>
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
      {activeTab === 'sentiment' && renderSentimentTab()}
      {activeTab === 'products' && renderProductsTab()}
      {activeTab === 'trends' && renderTrendsTab()}
    </div>
  )
}

export default Market
