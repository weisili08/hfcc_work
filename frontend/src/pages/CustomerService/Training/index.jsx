import { useState, useEffect } from 'react'
import { generateTraining, getTrainings } from '../../../services/csApi'
import './Training.css'

// 模拟培训课程数据
const MOCK_TRAININGS = [
  {
    training_id: 'train_001',
    title: '基金产品知识培训',
    type: 'product',
    difficulty: 'medium',
    status: 'active',
    description: '系统学习各类基金产品的特点、风险等级及适用人群',
    duration: 45,
    participant_count: 28,
    completion_rate: 85,
    created_at: '2026-04-10T10:00:00Z'
  },
  {
    training_id: 'train_002',
    title: '客户投诉处理技巧',
    type: 'complaint',
    difficulty: 'hard',
    status: 'active',
    description: '学习如何有效处理各类客户投诉，提升客户满意度',
    duration: 60,
    participant_count: 35,
    completion_rate: 72,
    created_at: '2026-04-08T14:00:00Z'
  },
  {
    training_id: 'train_003',
    title: '反洗钱合规培训',
    type: 'compliance',
    difficulty: 'medium',
    status: 'active',
    description: '了解反洗钱法规要求，掌握可疑交易识别方法',
    duration: 30,
    participant_count: 42,
    completion_rate: 95,
    created_at: '2026-04-05T09:00:00Z'
  },
  {
    training_id: 'train_004',
    title: '疑难问题应对实战',
    type: 'difficult',
    difficulty: 'hard',
    status: 'draft',
    description: '针对复杂业务场景的案例分析与应对策略',
    duration: 90,
    participant_count: 0,
    completion_rate: 0,
    created_at: '2026-04-15T16:00:00Z'
  },
  {
    training_id: 'train_005',
    title: '新客服入职培训',
    type: 'product',
    difficulty: 'easy',
    status: 'active',
    description: '新入职客服人员的基础业务知识培训',
    duration: 120,
    participant_count: 5,
    completion_rate: 60,
    created_at: '2026-04-12T08:00:00Z'
  }
]

// 模拟生成的培训内容
const MOCK_GENERATED_TRAINING = {
  training_id: 'train_new_001',
  scenario: {
    title: '基金赎回争议处理',
    background: '客户王先生于昨日提交基金赎回申请，但今日发现净值下跌，要求撤销赎回申请。根据基金交易规则，赎回申请一旦提交不可撤销。',
    customer_profile: {
      name: '王先生',
      age: 45,
      investment_experience: '3年',
      risk_tolerance: '中等',
      personality: '急躁，注重细节'
    }
  },
  dialogue: [
    {
      role: 'customer',
      content: '我要撤销昨天的赎回申请！今天净值跌了，我不想赎回了！',
      expected_response: '安抚情绪，解释规则，提供替代方案'
    },
    {
      role: 'agent',
      content: '王先生，我非常理解您的心情。看到净值下跌确实会让人感到遗憾。不过根据基金交易规则，赎回申请一旦提交是不能撤销的。',
      expected_response: '表达同理心，清晰说明规则'
    },
    {
      role: 'customer',
      content: '什么？不能撤销？你们这是什么霸王条款！我要投诉！',
      expected_response: '进一步安抚，详细解释，转介方案'
    },
    {
      role: 'agent',
      content: '王先生您先别急，我来详细解释一下。基金赎回遵循"未知价"原则，您提交申请时并不知道当天的净值。这个规则对所有投资者都是公平透明的。如果您看好后市，可以在资金到账后重新申购。',
      expected_response: '耐心解释规则，提供建设性建议'
    }
  ],
  evaluation_criteria: [
    '能否在第一时间安抚客户情绪',
    '是否清晰准确地解释了赎回规则',
    '是否提供了合理的替代方案',
    '沟通语气是否专业且富有同理心',
    '是否有效避免了投诉升级'
  ],
  knowledge_points: [
    '基金赎回的"未知价"原则',
    '赎回申请不可撤销的规则依据',
    '客户情绪安抚技巧',
    '投诉预防与升级处理'
  ]
}

const typeMap = {
  product: { label: '产品知识', color: '#3182ce' },
  complaint: { label: '投诉处理', color: '#e53e3e' },
  difficult: { label: '疑难问题', color: '#d69e2e' },
  compliance: { label: '合规培训', color: '#38a169' }
}

const difficultyMap = {
  easy: { label: '初级', color: '#52c41a' },
  medium: { label: '中级', color: '#1890ff' },
  hard: { label: '高级', color: '#722ed1' }
}

const statusMap = {
  active: { label: '进行中', color: '#52c41a' },
  draft: { label: '草稿', color: '#faad14' },
  archived: { label: '已归档', color: '#8c8c8c' }
}

function Training() {
  const [trainings, setTrainings] = useState(MOCK_TRAININGS)
  const [selectedTraining, setSelectedTraining] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState(null)
  const [generateForm, setGenerateForm] = useState({
    training_type: 'product',
    difficulty: 'medium',
    topic: ''
  })

  // 加载培训数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getTrainings()
        if (res?.data?.items) {
          setTrainings(res.data.items)
        }
      } catch (e) {
        console.log('Using mock training data')
      }
    }
    fetchData()
  }, [])

  const handleGenerate = async () => {
    setIsGenerating(true)
    setGeneratedContent(null)

    try {
      const res = await generateTraining({
        training_type: generateForm.training_type,
        difficulty: generateForm.difficulty,
        topic: generateForm.topic,
        trainee_id: 'agent_001'
      })

      if (res?.data) {
        setGeneratedContent(res.data)
      }
    } catch (e) {
      console.log('Using mock generated training')
      setTimeout(() => {
        setGeneratedContent({
          ...MOCK_GENERATED_TRAINING,
          scenario: {
            ...MOCK_GENERATED_TRAINING.scenario,
            title: generateForm.topic || MOCK_GENERATED_TRAINING.scenario.title
          }
        })
      }, 2000)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleViewDetail = (training) => {
    setSelectedTraining(training)
  }

  const handleBackToList = () => {
    setSelectedTraining(null)
    setGeneratedContent(null)
  }

  return (
    <div className="training-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">培训管理</h1>
        <p className="page-subtitle">AI陪练场景生成、培训课程管理</p>
      </div>

      {!selectedTraining ? (
        <>
          {/* AI生成培训内容 */}
          <div className="generate-section">
            <div className="section-card">
              <h3 className="section-title">🤖 AI生成培训内容</h3>
              <div className="generate-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>培训类型</label>
                    <select
                      value={generateForm.training_type}
                      onChange={(e) => setGenerateForm({...generateForm, training_type: e.target.value})}
                    >
                      <option value="product">产品知识</option>
                      <option value="complaint">投诉处理</option>
                      <option value="difficult">疑难问题</option>
                      <option value="compliance">合规培训</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>难度等级</label>
                    <select
                      value={generateForm.difficulty}
                      onChange={(e) => setGenerateForm({...generateForm, difficulty: e.target.value})}
                    >
                      <option value="easy">初级</option>
                      <option value="medium">中级</option>
                      <option value="hard">高级</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>培训主题（可选）</label>
                  <input
                    type="text"
                    value={generateForm.topic}
                    onChange={(e) => setGenerateForm({...generateForm, topic: e.target.value})}
                    placeholder="输入具体的培训主题，如：基金赎回争议处理"
                  />
                </div>
                <button
                  className="generate-btn"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <span className="spinner"></span>
                      AI生成中...
                    </>
                  ) : (
                    <>
                      <span>✨</span> 生成培训内容
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* 生成的培训内容预览 */}
            {generatedContent && (
              <div className="section-card generated-preview">
                <div className="preview-header">
                  <h4>生成的培训场景：{generatedContent.scenario.title}</h4>
                  <button 
                    className="view-detail-btn"
                    onClick={() => setSelectedTraining({ ...generatedContent, isGenerated: true })}
                  >
                    查看详情 →
                  </button>
                </div>
                <p className="preview-desc">{generatedContent.scenario.background}</p>
                <div className="preview-stats">
                  <span>对话轮次: {generatedContent.dialogue.length}</span>
                  <span>知识点: {generatedContent.knowledge_points.length}个</span>
                </div>
              </div>
            )}
          </div>

          {/* 培训课程列表 */}
          <div className="training-list-section">
            <h3 className="section-title">培训课程</h3>
            <div className="training-grid">
              {trainings.map(training => (
                <div 
                  key={training.training_id} 
                  className="training-card"
                  onClick={() => handleViewDetail(training)}
                >
                  <div className="training-card-header">
                    <span 
                      className="type-tag"
                      style={{ 
                        backgroundColor: `${typeMap[training.type]?.color}20`,
                        color: typeMap[training.type]?.color 
                      }}
                    >
                      {typeMap[training.type]?.label}
                    </span>
                    <span 
                      className="difficulty-tag"
                      style={{ color: difficultyMap[training.difficulty]?.color }}
                    >
                      {difficultyMap[training.difficulty]?.label}
                    </span>
                  </div>
                  <h4 className="training-title">{training.title}</h4>
                  <p className="training-desc">{training.description}</p>
                  <div className="training-meta">
                    <span className="duration">⏱️ {training.duration}分钟</span>
                    <span 
                      className="status-badge"
                      style={{ color: statusMap[training.status]?.color }}
                    >
                      {statusMap[training.status]?.label}
                    </span>
                  </div>
                  {training.status === 'active' && (
                    <div className="training-progress">
                      <div className="progress-info">
                        <span>完成率 {training.completion_rate}%</span>
                        <span>{training.participant_count}人参与</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${training.completion_rate}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        /* 培训详情页 */
        <div className="training-detail">
          <div className="detail-header">
            <button className="back-btn" onClick={handleBackToList}>
              ← 返回列表
            </button>
            <h2>{selectedTraining.isGenerated ? selectedTraining.scenario.title : selectedTraining.title}</h2>
          </div>

          {selectedTraining.isGenerated ? (
            /* AI生成的培训内容详情 */
            <div className="detail-content">
              {/* 场景背景 */}
              <div className="detail-section">
                <h3>📋 场景背景</h3>
                <p>{selectedTraining.scenario.background}</p>
              </div>

              {/* 客户画像 */}
              <div className="detail-section">
                <h3>👤 客户画像</h3>
                <div className="profile-grid">
                  <div className="profile-item">
                    <span className="label">姓名</span>
                    <span className="value">{selectedTraining.scenario.customer_profile.name}</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">年龄</span>
                    <span className="value">{selectedTraining.scenario.customer_profile.age}岁</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">投资经验</span>
                    <span className="value">{selectedTraining.scenario.customer_profile.investment_experience}</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">风险偏好</span>
                    <span className="value">{selectedTraining.scenario.customer_profile.risk_tolerance}</span>
                  </div>
                  <div className="profile-item full-width">
                    <span className="label">性格特点</span>
                    <span className="value">{selectedTraining.scenario.customer_profile.personality}</span>
                  </div>
                </div>
              </div>

              {/* 对话脚本 */}
              <div className="detail-section">
                <h3>💬 对话脚本</h3>
                <div className="dialogue-list">
                  {selectedTraining.dialogue.map((item, idx) => (
                    <div key={idx} className={`dialogue-item ${item.role}`}>
                      <div className="dialogue-avatar">
                        {item.role === 'customer' ? '👤' : '🎧'}
                      </div>
                      <div className="dialogue-content">
                        <div className="dialogue-role">
                          {item.role === 'customer' ? '客户' : '客服'}
                        </div>
                        <div className="dialogue-text">{item.content}</div>
                        {item.expected_response && (
                          <div className="expected-response">
                            <span>期望回应要点：</span>{item.expected_response}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 评分标准 */}
              <div className="detail-section">
                <h3>📊 评分标准</h3>
                <ul className="criteria-list">
                  {selectedTraining.evaluation_criteria.map((criteria, idx) => (
                    <li key={idx}>{criteria}</li>
                  ))}
                </ul>
              </div>

              {/* 知识点 */}
              <div className="detail-section">
                <h3>📚 涉及知识点</h3>
                <div className="knowledge-tags">
                  {selectedTraining.knowledge_points.map((point, idx) => (
                    <span key={idx} className="knowledge-tag">{point}</span>
                  ))}
                </div>
              </div>

              {/* 开始培训按钮 */}
              <div className="detail-actions">
                <button className="start-training-btn">
                  🚀 开始培训
                </button>
                <button className="save-draft-btn">
                  💾 保存为草稿
                </button>
              </div>
            </div>
          ) : (
            /* 普通培训课程详情 */
            <div className="detail-content">
              <div className="detail-section">
                <h3>课程介绍</h3>
                <p>{selectedTraining.description}</p>
              </div>
              <div className="detail-section">
                <h3>课程信息</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">培训类型</span>
                    <span className="value">{typeMap[selectedTraining.type]?.label}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">难度等级</span>
                    <span className="value">{difficultyMap[selectedTraining.difficulty]?.label}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">课程时长</span>
                    <span className="value">{selectedTraining.duration}分钟</span>
                  </div>
                  <div className="info-item">
                    <span className="label">参与人数</span>
                    <span className="value">{selectedTraining.participant_count}人</span>
                  </div>
                  <div className="info-item">
                    <span className="label">完成率</span>
                    <span className="value">{selectedTraining.completion_rate}%</span>
                  </div>
                </div>
              </div>
              <div className="detail-actions">
                <button className="start-training-btn">
                  🚀 开始学习
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Training
