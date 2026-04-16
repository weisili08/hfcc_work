import { useState, useEffect } from 'react'
import { generateEducationContent, amlCheck, getRiskTips } from '../../services/educationApi'
import './Education.css'

// Tab配置
const TABS = [
  { key: 'content', label: '投教内容', icon: '📚' },
  { key: 'compliance', label: '合规检查', icon: '✅' },
  { key: 'risks', label: '风险提示', icon: '⚠️' }
]

// 模拟投教内容数据
const MOCK_EDUCATION_CONTENTS = [
  {
    content_id: 'edu_001',
    title: '基金投资入门指南',
    difficulty_level: 'beginner',
    content_format: 'article',
    summary: '为投资新手介绍基金的基本概念、分类及投资要点',
    key_points: ['基金的定义与分类', '如何选择适合自己的基金', '基金投资的风险与收益'],
    created_at: '2026-04-10T10:00:00Z'
  },
  {
    content_id: 'edu_002',
    title: '定投策略详解',
    difficulty_level: 'intermediate',
    content_format: 'video',
    summary: '深入讲解基金定投的原理、优势及实操技巧',
    key_points: ['定投的复利效应', '定投时机的选择', '定投组合的构建'],
    created_at: '2026-04-08T14:00:00Z'
  },
  {
    content_id: 'edu_003',
    title: '资产配置高级策略',
    difficulty_level: 'advanced',
    content_format: 'infographic',
    summary: '面向高阶投资者的资产配置理论与实践',
    key_points: ['现代投资组合理论', '风险平价策略', '动态再平衡方法'],
    created_at: '2026-04-05T09:00:00Z'
  }
]

// 模拟合规检查结果
const MOCK_COMPLIANCE_RESULT = {
  check_id: 'check_001',
  check_type: 'content',
  status: 'completed',
  overall_risk_level: 'warning',
  risk_indicators: [
    {
      indicator_code: 'R001',
      indicator_name: '收益承诺风险',
      risk_level: 'high',
      description: '内容中包含"保证收益"等违规表述',
      triggered_rules: ['禁止承诺保本保收益']
    },
    {
      indicator_code: 'R002',
      indicator_name: '风险提示不足',
      risk_level: 'medium',
      description: '未充分提示投资风险',
      triggered_rules: ['必须充分揭示投资风险']
    }
  ],
  recommendations: [
    '删除"保证收益"等违规表述',
    '在显著位置添加风险提示',
    '补充产品风险等级说明'
  ]
}

// 模拟风险提示数据
const MOCK_RISK_TIPS = [
  {
    tip_id: 'tip_001',
    scenario: '产品推荐',
    risk_type: '适当性风险',
    risk_description: '向风险承受能力不匹配的客户推荐高风险产品',
    regulatory_requirement: '必须执行投资者适当性管理',
    suggested_script: '根据您的风险评估结果，这款产品可能不适合您。我建议您考虑风险等级更低的产品。',
    severity: 'high'
  },
  {
    tip_id: 'tip_002',
    scenario: '收益说明',
    risk_type: '误导性陈述',
    risk_description: '使用历史业绩暗示未来收益',
    regulatory_requirement: '禁止承诺或暗示收益',
    suggested_script: '历史业绩不代表未来表现，投资有风险，入市需谨慎。',
    severity: 'high'
  },
  {
    tip_id: 'tip_003',
    scenario: '客户信息',
    risk_type: '信息保护',
    risk_description: '客户敏感信息泄露风险',
    regulatory_requirement: '严格保护客户信息安全',
    suggested_script: '您的信息我们将严格保密，仅用于业务办理。',
    severity: 'medium'
  },
  {
    tip_id: 'tip_004',
    scenario: '投诉处理',
    risk_type: '合规操作',
    risk_description: '投诉处理不当引发监管风险',
    regulatory_requirement: '妥善处理客户投诉',
    suggested_script: '感谢您的反馈，我们会认真调查并在3个工作日内给您答复。',
    severity: 'medium'
  }
]

const difficultyMap = {
  beginner: { label: '入门级', color: '#52c41a' },
  intermediate: { label: '进阶级', color: '#1890ff' },
  advanced: { label: '高级', color: '#722ed1' }
}

const formatMap = {
  article: { label: '文章', icon: '📄' },
  video: { label: '视频', icon: '🎬' },
  infographic: { label: '图文', icon: '📊' },
  quiz: { label: '测试', icon: '❓' }
}

const severityMap = {
  high: { label: '严重', color: '#ff4d4f' },
  medium: { label: '一般', color: '#faad14' },
  low: { label: '轻微', color: '#52c41a' }
}

function Education() {
  const [activeTab, setActiveTab] = useState('content')
  const [contents, setContents] = useState(MOCK_EDUCATION_CONTENTS)
  const [generatedContent, setGeneratedContent] = useState(null)
  const [isGeneratingContent, setIsGeneratingContent] = useState(false)
  const [contentForm, setContentForm] = useState({
    topic: '',
    difficulty_level: 'beginner',
    content_format: 'article'
  })
  const [complianceText, setComplianceText] = useState('')
  const [complianceResult, setComplianceResult] = useState(null)
  const [isChecking, setIsChecking] = useState(false)
  const [riskTips, setRiskTips] = useState(MOCK_RISK_TIPS)

  // 加载数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getRiskTips()
        if (res?.data?.tips) {
          setRiskTips(res.data.tips)
        }
      } catch (e) {
        console.log('Using mock risk tips')
      }
    }
    fetchData()
  }, [])

  // 生成投教内容
  const handleGenerateContent = async () => {
    if (!contentForm.topic) {
      alert('请输入投教主题')
      return
    }

    setIsGeneratingContent(true)
    try {
      const res = await generateEducationContent({
        topic: contentForm.topic,
        difficulty_level: contentForm.difficulty_level,
        content_format: contentForm.content_format
      })
      if (res?.data) {
        setGeneratedContent(res.data)
      }
    } catch (e) {
      console.log('Using mock generated content')
      setTimeout(() => {
        setGeneratedContent({
          content_id: `edu_${Date.now()}`,
          topic: contentForm.topic,
          difficulty_level: contentForm.difficulty_level,
          content: {
            title: contentForm.topic,
            summary: `这是一篇关于${contentForm.topic}的投教内容，适合${difficultyMap[contentForm.difficulty_level].label}投资者阅读。`,
            body: `## 什么是${contentForm.topic}\n\n${contentForm.topic}是投资者教育的重要内容...\n\n## 核心要点\n\n1. 理解基本概念\n2. 掌握投资方法\n3. 认识投资风险\n\n## 总结\n\n通过本文的学习，您应该对${contentForm.topic}有了基本的了解...`,
            key_points: ['核心概念理解', '实操技巧掌握', '风险意识培养'],
            risk_warnings: ['投资有风险，入市需谨慎', '历史业绩不代表未来表现'],
            related_concepts: ['基金基础知识', '投资组合理论']
          }
        })
      }, 1500)
    } finally {
      setIsGeneratingContent(false)
    }
  }

  // 合规检查
  const handleComplianceCheck = async () => {
    if (!complianceText.trim()) {
      alert('请输入待检内容')
      return
    }

    setIsChecking(true)
    setComplianceResult(null)

    try {
      const res = await amlCheck({
        check_type: 'content',
        check_scope: { content: complianceText }
      })
      if (res?.data) {
        setComplianceResult(res.data)
      }
    } catch (e) {
      console.log('Using mock compliance result')
      setTimeout(() => {
        setComplianceResult(MOCK_COMPLIANCE_RESULT)
      }, 1500)
    } finally {
      setIsChecking(false)
    }
  }

  // 渲染投教内容Tab
  const renderContentTab = () => (
    <div className="tab-content">
      {/* AI生成投教内容 */}
      <div className="generate-section">
        <div className="section-card">
          <h3>🤖 AI生成投教内容</h3>
          <div className="generate-form">
            <div className="form-group">
              <label>投教主题</label>
              <input
                type="text"
                value={contentForm.topic}
                onChange={(e) => setContentForm({...contentForm, topic: e.target.value})}
                placeholder="输入投教主题，如：基金定投入门"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>难度等级</label>
                <select
                  value={contentForm.difficulty_level}
                  onChange={(e) => setContentForm({...contentForm, difficulty_level: e.target.value})}
                >
                  <option value="beginner">入门级</option>
                  <option value="intermediate">进阶级</option>
                  <option value="advanced">高级</option>
                </select>
              </div>
              <div className="form-group">
                <label>内容形式</label>
                <select
                  value={contentForm.content_format}
                  onChange={(e) => setContentForm({...contentForm, content_format: e.target.value})}
                >
                  <option value="article">文章</option>
                  <option value="video">视频脚本</option>
                  <option value="infographic">图文</option>
                  <option value="quiz">测试题</option>
                </select>
              </div>
            </div>
            <button
              className="generate-btn"
              onClick={handleGenerateContent}
              disabled={isGeneratingContent}
            >
              {isGeneratingContent ? 'AI生成中...' : '✨ 生成投教内容'}
            </button>
          </div>
        </div>

        {/* 生成的内容预览 */}
        {generatedContent && (
          <div className="section-card content-preview">
            <div className="preview-header">
              <h4>{generatedContent.content?.title || generatedContent.topic}</h4>
              <div className="preview-tags">
                <span 
                  className="difficulty-tag"
                  style={{ color: difficultyMap[generatedContent.difficulty_level]?.color }}
                >
                  {difficultyMap[generatedContent.difficulty_level]?.label}
                </span>
              </div>
            </div>
            <p className="preview-summary">{generatedContent.content?.summary}</p>
            {generatedContent.content?.key_points && (
              <div className="key-points">
                <h5>核心要点</h5>
                <ul>
                  {generatedContent.content.key_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="preview-actions">
              <button className="action-btn primary">查看完整内容</button>
              <button className="action-btn">保存到素材库</button>
            </div>
          </div>
        )}
      </div>

      {/* 投教内容列表 */}
      <div className="content-list-section">
        <h3>投教内容库</h3>
        <div className="content-grid">
          {contents.map(content => (
            <div key={content.content_id} className="content-card">
              <div className="content-header">
                <span className="format-icon">{formatMap[content.content_format]?.icon}</span>
                <span 
                  className="difficulty-badge"
                  style={{ color: difficultyMap[content.difficulty_level]?.color }}
                >
                  {difficultyMap[content.difficulty_level]?.label}
                </span>
              </div>
              <h4>{content.title}</h4>
              <p>{content.summary}</p>
              <div className="content-keypoints">
                {content.key_points.slice(0, 2).map((point, idx) => (
                  <span key={idx} className="keypoint-tag">{point}</span>
                ))}
              </div>
              <div className="content-footer">
                <span>{new Date(content.created_at).toLocaleDateString('zh-CN')}</span>
                <button className="view-btn">查看</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  // 渲染合规检查Tab
  const renderComplianceTab = () => (
    <div className="tab-content">
      <div className="compliance-panel">
        <div className="section-card">
          <h3>🔍 AI合规检查</h3>
          <div className="compliance-input">
            <label>输入待检内容</label>
            <textarea
              rows={8}
              value={complianceText}
              onChange={(e) => setComplianceText(e.target.value)}
              placeholder="粘贴需要检查的文案内容，AI将自动识别合规风险..."
            />
            <button
              className="check-btn"
              onClick={handleComplianceCheck}
              disabled={isChecking || !complianceText.trim()}
            >
              {isChecking ? 'AI检查中...' : '✅ 开始合规检查'}
            </button>
          </div>
        </div>

        {/* 检查结果 */}
        {complianceResult && (
          <div className={`section-card check-result ${complianceResult.overall_risk_level}`}>
            <div className="result-header">
              <h4>检查结果</h4>
              <span className={`result-badge ${complianceResult.overall_risk_level}`}>
                {complianceResult.overall_risk_level === 'pass' ? '✅ 通过' : 
                 complianceResult.overall_risk_level === 'warning' ? '⚠️ 警告' : '❌ 违规'}
              </span>
            </div>

            {complianceResult.risk_indicators.length > 0 && (
              <div className="risk-indicators">
                <h5>风险指标</h5>
                {complianceResult.risk_indicators.map((indicator, idx) => (
                  <div key={idx} className={`indicator-item ${indicator.risk_level}`}>
                    <div className="indicator-header">
                      <span className="indicator-code">{indicator.indicator_code}</span>
                      <span className="indicator-name">{indicator.indicator_name}</span>
                      <span 
                        className="risk-level-badge"
                        style={{ color: severityMap[indicator.risk_level]?.color }}
                      >
                        {severityMap[indicator.risk_level]?.label}
                      </span>
                    </div>
                    <p className="indicator-desc">{indicator.description}</p>
                    <div className="triggered-rules">
                      {indicator.triggered_rules.map((rule, ridx) => (
                        <span key={ridx} className="rule-tag">{rule}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="recommendations">
              <h5>修改建议</h5>
              <ul>
                {complianceResult.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  // 渲染风险提示Tab
  const renderRisksTab = () => (
    <div className="tab-content">
      <div className="risks-panel">
        <h3>合规风险提示库</h3>
        <div className="risks-list">
          {riskTips.map(tip => (
            <div key={tip.tip_id} className={`risk-tip-card ${tip.severity}`}>
              <div className="tip-header">
                <div className="tip-scenario">
                  <span className="scenario-label">{tip.scenario}</span>
                  <span 
                    className="severity-badge"
                    style={{ color: severityMap[tip.severity]?.color }}
                  >
                    {severityMap[tip.severity]?.label}
                  </span>
                </div>
                <h4>{tip.risk_type}</h4>
              </div>
              <div className="tip-body">
                <div className="tip-section">
                  <label>风险描述</label>
                  <p>{tip.risk_description}</p>
                </div>
                <div className="tip-section">
                  <label>监管要求</label>
                  <p>{tip.regulatory_requirement}</p>
                </div>
                <div className="tip-section">
                  <label>建议话术</label>
                  <div className="script-box">{tip.suggested_script}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="education-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">投教与合规</h1>
        <p className="page-subtitle">投资者教育内容、合规检查、风险提示</p>
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
      {activeTab === 'content' && renderContentTab()}
      {activeTab === 'compliance' && renderComplianceTab()}
      {activeTab === 'risks' && renderRisksTab()}
    </div>
  )
}

export default Education
