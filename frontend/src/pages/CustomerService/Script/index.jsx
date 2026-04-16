import { useState } from 'react'
import { generateSpeech } from '../../../services/csApi'
import './Script.css'

// 场景选项
const scenarioOptions = [
  { value: 'comfort', label: '投诉安抚', icon: '🤗', description: '安抚情绪激动的客户' },
  { value: 'explain', label: '产品解释', icon: '📋', description: '解释产品相关疑问' },
  { value: 'guide', label: '客户挽留', icon: '🤝', description: '挽留意向流失客户' },
  { value: 'apologize', label: '道歉致歉', icon: '🙏', description: '正式道歉场景' },
  { value: 'recommend', label: '产品推荐', icon: '💡', description: '推荐适合的产品' }
]

// 风格选项
const toneOptions = [
  { value: 'professional', label: '专业正式', description: '规范、严谨的专业话术' },
  { value: 'warm', label: '温暖亲切', description: '友好、有温度的话术' },
  { value: 'firm', label: '坚定明确', description: '立场清晰、态度明确' }
]

// 模拟生成结果
const MOCK_GENERATED_SPEECH = {
  speech_id: 'speech_001',
  opening: '您好，非常感谢您拨打我们的客服热线。我是客服专员小李，很高兴为您服务。',
  body: '我完全理解您现在的心情，遇到这样的问题确实让人感到困扰。请您放心，我们会认真对待您的反馈，并尽全力帮您解决。\n\n关于您提到的情况，我已经详细记录下来了。根据我们的处理流程，这个问题会在24小时内得到响应，3个工作日内给出解决方案。\n\n在此期间，如果您有任何疑问，可以随时联系我，我的工号是10086。',
  closing: '再次感谢您的理解与支持，祝您生活愉快！',
  word_count: 186,
  disclaimer: '以上话术仅供参考，实际使用时请根据具体情况调整。',
  notes: [
    '注意语速适中，保持平和的语调',
    '适当使用停顿，给客户思考时间',
    '关键信息需要确认客户已理解'
  ]
}

function Script() {
  const [selectedScenario, setSelectedScenario] = useState('comfort')
  const [selectedTone, setSelectedTone] = useState('professional')
  const [customerIssue, setCustomerIssue] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedSpeech, setGeneratedSpeech] = useState(null)
  const [rating, setRating] = useState(0)

  const handleGenerate = async () => {
    if (!customerIssue.trim()) {
      alert('请输入客户情况描述')
      return
    }

    setIsGenerating(true)
    setGeneratedSpeech(null)

    try {
      const res = await generateSpeech({
        scenario: selectedScenario,
        customer_issue: customerIssue,
        tone: selectedTone,
        generate_count: 1
      })

      if (res?.data?.speeches?.[0]) {
        setGeneratedSpeech(res.data.speeches[0])
      }
    } catch (e) {
      console.log('Using mock speech data')
      // 模拟延迟
      setTimeout(() => {
        setGeneratedSpeech({
          ...MOCK_GENERATED_SPEECH,
          body: MOCK_GENERATED_SPEECH.body.replace('您提到的情况', customerIssue.slice(0, 20))
        })
      }, 1500)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  }

  const handleCopyAll = () => {
    if (!generatedSpeech) return
    const fullText = `${generatedSpeech.opening}\n\n${generatedSpeech.body}\n\n${generatedSpeech.closing}`
    navigator.clipboard.writeText(fullText)
    alert('完整话术已复制到剪贴板')
  }

  return (
    <div className="script-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">话术生成</h1>
        <p className="page-subtitle">AI智能生成标准化客服话术</p>
      </div>

      <div className="script-container">
        {/* 左侧配置区 */}
        <div className="script-config">
          {/* 场景选择 */}
          <div className="config-section">
            <h3 className="config-title">选择场景</h3>
            <div className="scenario-grid">
              {scenarioOptions.map(option => (
                <div
                  key={option.value}
                  className={`scenario-card ${selectedScenario === option.value ? 'active' : ''}`}
                  onClick={() => setSelectedScenario(option.value)}
                >
                  <div className="scenario-icon">{option.icon}</div>
                  <div className="scenario-info">
                    <div className="scenario-label">{option.label}</div>
                    <div className="scenario-desc">{option.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 风格选择 */}
          <div className="config-section">
            <h3 className="config-title">选择风格</h3>
            <div className="tone-list">
              {toneOptions.map(option => (
                <div
                  key={option.value}
                  className={`tone-item ${selectedTone === option.value ? 'active' : ''}`}
                  onClick={() => setSelectedTone(option.value)}
                >
                  <div className="tone-radio">
                    <div className="tone-radio-inner"></div>
                  </div>
                  <div className="tone-info">
                    <div className="tone-label">{option.label}</div>
                    <div className="tone-desc">{option.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 客户情况输入 */}
          <div className="config-section">
            <h3 className="config-title">客户情况描述</h3>
            <textarea
              className="issue-textarea"
              rows={5}
              value={customerIssue}
              onChange={(e) => setCustomerIssue(e.target.value)}
              placeholder="请描述客户的情况、问题或需求，AI将根据场景生成合适的话术..."
            />
            <div className="textarea-hint">
              建议包含：客户情绪状态、主要诉求、相关背景信息
            </div>
          </div>

          {/* 生成按钮 */}
          <button
            className="generate-btn"
            onClick={handleGenerate}
            disabled={isGenerating || !customerIssue.trim()}
          >
            {isGenerating ? (
              <>
                <span className="spinner"></span>
                AI生成中...
              </>
            ) : (
              <>
                <span>✨</span> 生成话术
              </>
            )}
          </button>
        </div>

        {/* 右侧结果区 */}
        <div className="script-result">
          {!generatedSpeech && !isGenerating && (
            <div className="empty-result">
              <div className="empty-icon">🎤</div>
              <div className="empty-title">话术生成结果</div>
              <div className="empty-desc">
                在左侧选择场景、风格并输入客户情况后<br />
                点击"生成话术"按钮获取AI生成的话术
              </div>
            </div>
          )}

          {isGenerating && (
            <div className="generating-state">
              <div className="generating-animation">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="generating-text">AI正在分析场景并生成话术...</div>
              <div className="generating-subtext">请稍候，这通常需要几秒钟</div>
            </div>
          )}

          {generatedSpeech && !isGenerating && (
            <div className="result-content">
              <div className="result-header">
                <h3 className="result-title">生成结果</h3>
                <div className="result-actions">
                  <button className="result-action-btn" onClick={handleCopyAll}>
                    📋 复制全部
                  </button>
                  <button className="result-action-btn" onClick={handleGenerate}>
                    🔄 重新生成
                  </button>
                </div>
              </div>

              {/* 开场白 */}
              <div className="speech-section">
                <div className="section-header-row">
                  <h4 className="section-label">开场白</h4>
                  <button 
                    className="copy-btn"
                    onClick={() => handleCopy(generatedSpeech.opening)}
                  >
                    复制
                  </button>
                </div>
                <div className="speech-box opening">
                  {generatedSpeech.opening}
                </div>
              </div>

              {/* 核心话术 */}
              <div className="speech-section">
                <div className="section-header-row">
                  <h4 className="section-label">核心话术</h4>
                  <button 
                    className="copy-btn"
                    onClick={() => handleCopy(generatedSpeech.body)}
                  >
                    复制
                  </button>
                </div>
                <div className="speech-box body">
                  {generatedSpeech.body.split('\n').map((paragraph, idx) => (
                    <p key={idx}>{paragraph}</p>
                  ))}
                </div>
              </div>

              {/* 结束语 */}
              <div className="speech-section">
                <div className="section-header-row">
                  <h4 className="section-label">结束语</h4>
                  <button 
                    className="copy-btn"
                    onClick={() => handleCopy(generatedSpeech.closing)}
                  >
                    复制
                  </button>
                </div>
                <div className="speech-box closing">
                  {generatedSpeech.closing}
                </div>
              </div>

              {/* 注意事项 */}
              {generatedSpeech.notes && (
                <div className="speech-section">
                  <h4 className="section-label">注意事项</h4>
                  <div className="notes-box">
                    <ul>
                      {generatedSpeech.notes.map((note, idx) => (
                        <li key={idx}>{note}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* 免责声明 */}
              <div className="disclaimer">
                ⚠️ {generatedSpeech.disclaimer}
              </div>

              {/* 评分 */}
              <div className="rating-section">
                <div className="rating-label">对话术满意吗？</div>
                <div className="rating-stars">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      className={`star-btn ${rating >= star ? 'active' : ''}`}
                      onClick={() => setRating(star)}
                    >
                      ★
                    </button>
                  ))}
                </div>
                {rating > 0 && (
                  <div className="rating-thanks">
                    感谢您的评价！
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Script
