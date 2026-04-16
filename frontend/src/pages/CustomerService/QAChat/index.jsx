import { useState, useRef, useEffect } from 'react'
import { qaChat, getQASessions, createQASession, deleteQASession } from '../../../services/csApi'
import './QAChat.css'

// 模拟会话列表数据
const MOCK_SESSIONS = [
  {
    session_id: 'sess_001',
    title: '基金申购费率咨询',
    last_message: 'XX基金的申购费率是多少？',
    updated_at: '2026-04-16T10:30:00Z',
    message_count: 5
  },
  {
    session_id: 'sess_002',
    title: '赎回流程咨询',
    last_message: '如何办理基金赎回？',
    updated_at: '2026-04-16T09:15:00Z',
    message_count: 3
  },
  {
    session_id: 'sess_003',
    title: '定投设置问题',
    last_message: '定投可以随时修改金额吗？',
    updated_at: '2026-04-15T16:45:00Z',
    message_count: 8
  }
]

// 模拟消息数据
const MOCK_MESSAGES = {
  'sess_001': [
    {
      id: 1,
      type: 'user',
      content: 'XX基金的申购费率是多少？',
      timestamp: '10:30'
    },
    {
      id: 2,
      type: 'ai',
      content: 'XX稳健增长混合基金（代码XXXXXX）申购费率如下：\n\n• 申购金额 < 100万：1.50%\n• 100万 ≤ 金额 < 500万：1.00%\n• 金额 ≥ 500万：1000元/笔',
      source: 'XX稳健增长混合基金招募说明书',
      section: '第6章 基金份额的申购与赎回',
      confidence: 0.95,
      aiGenerated: true,
      timestamp: '10:30'
    }
  ],
  'sess_002': [
    {
      id: 1,
      type: 'user',
      content: '如何办理基金赎回？',
      timestamp: '09:15'
    },
    {
      id: 2,
      type: 'ai',
      content: '您可以通过以下渠道办理基金赎回：\n\n1. **网上交易平台**：登录官网或APP，在"我的持仓"中选择要赎回的基金\n2. **电话委托**：拨打客服热线400-XXX-XXXX\n3. **柜台办理**：携带身份证件前往营业网点\n\n赎回资金一般T+3个工作日到账。',
      source: '基金业务操作手册',
      section: '赎回业务办理流程',
      confidence: 0.92,
      aiGenerated: true,
      timestamp: '09:15'
    }
  ],
  'sess_003': [
    {
      id: 1,
      type: 'user',
      content: '定投可以随时修改金额吗？',
      timestamp: '16:45'
    },
    {
      id: 2,
      type: 'ai',
      content: '是的，定投金额可以随时修改。您可以通过以下方式调整：\n\n• 登录网上交易平台，在"定投管理"中修改\n• 拨打客服热线进行修改\n• 前往柜台办理\n\n修改将在下一个扣款日生效。',
      source: '定投业务规则说明',
      section: '定投协议变更',
      confidence: 0.88,
      aiGenerated: true,
      timestamp: '16:45'
    }
  ]
}

// 快捷问题
const quickQuestions = [
  '什么是货币基金？',
  '如何办理赎回？',
  '基金净值查询',
  '风险评估流程',
  '定投如何设置？',
  '申购费率是多少？'
]

function QAChat() {
  const [sessions, setSessions] = useState(MOCK_SESSIONS)
  const [currentSessionId, setCurrentSessionId] = useState('sess_001')
  const [messages, setMessages] = useState(MOCK_MESSAGES['sess_001'])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const messagesEndRef = useRef(null)

  // 加载会话列表
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await getQASessions()
        if (res?.data?.items) {
          setSessions(res.data.items)
        }
      } catch (e) {
        console.log('Using mock sessions')
      }
    }
    fetchSessions()
  }, [])

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 切换会话
  const handleSessionChange = (sessionId) => {
    setCurrentSessionId(sessionId)
    setMessages(MOCK_MESSAGES[sessionId] || [])
  }

  // 创建新会话
  const handleNewSession = async () => {
    const newSession = {
      session_id: `sess_${Date.now()}`,
      title: '新会话',
      last_message: '',
      updated_at: new Date().toISOString(),
      message_count: 0
    }
    
    try {
      const res = await createQASession({ title: '新会话' })
      if (res?.data) {
        setSessions([res.data, ...sessions])
        setCurrentSessionId(res.data.session_id)
        setMessages([])
      }
    } catch (e) {
      // 使用模拟数据
      setSessions([newSession, ...sessions])
      setCurrentSessionId(newSession.session_id)
      setMessages([])
    }
  }

  // 删除会话
  const handleDeleteSession = async (e, sessionId) => {
    e.stopPropagation()
    
    try {
      await deleteQASession(sessionId)
    } catch (e) {
      console.log('Delete session failed, using local')
    }
    
    const newSessions = sessions.filter(s => s.session_id !== sessionId)
    setSessions(newSessions)
    
    if (currentSessionId === sessionId && newSessions.length > 0) {
      setCurrentSessionId(newSessions[0].session_id)
      setMessages(MOCK_MESSAGES[newSessions[0].session_id] || [])
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim()) return

    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // 更新会话最后消息
    setSessions(prev => prev.map(s => 
      s.session_id === currentSessionId 
        ? { ...s, last_message: inputValue, updated_at: new Date().toISOString() }
        : s
    ))

    // 调用API获取AI回复
    try {
      const res = await qaChat({
        query: inputValue,
        session_id: currentSessionId,
        user_id: 'agent_001'
      })
      
      if (res?.data) {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: res.data.answer_text,
          source: res.data.source_refs?.[0]?.doc_name || '知识库',
          section: res.data.source_refs?.[0]?.section || '',
          confidence: res.data.confidence,
          aiGenerated: res.data.ai_generated,
          timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (e) {
      // 模拟AI回复
      setTimeout(() => {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: `我理解您的问题是："${inputValue}"\n\n这是一个模拟的AI回复。在实际应用中，这里会调用后端API获取智能问答结果。系统会根据知识库内容为您提供准确的答案。`,
          source: '知识库',
          section: '相关章节',
          confidence: 0.88,
          aiGenerated: true,
          timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        }
        setMessages(prev => [...prev, aiMessage])
      }, 1500)
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickQuestion = (question) => {
    setInputValue(question)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="qa-chat">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">智能问答</h1>
        <p className="page-subtitle">基于知识库的自然语言问答，支持多轮对话</p>
      </div>

      {/* 聊天主区域 */}
      <div className="chat-wrapper">
        {/* 左侧会话列表 */}
        <div className={`chat-sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-header">
            <button className="new-session-btn" onClick={handleNewSession}>
              <span>+</span> 新会话
            </button>
            <button 
              className="collapse-btn"
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            >
              {isSidebarCollapsed ? '→' : '←'}
            </button>
          </div>
          
          <div className="sessions-list">
            {sessions.map(session => (
              <div
                key={session.session_id}
                className={`session-item ${currentSessionId === session.session_id ? 'active' : ''}`}
                onClick={() => handleSessionChange(session.session_id)}
              >
                <div className="session-icon">💬</div>
                <div className="session-info">
                  <div className="session-title">{session.title}</div>
                  <div className="session-preview">{session.last_message || '暂无消息'}</div>
                </div>
                <div className="session-meta">
                  <div className="session-time">{formatTime(session.updated_at)}</div>
                  <button 
                    className="session-delete"
                    onClick={(e) => handleDeleteSession(e, session.session_id)}
                    title="删除会话"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧聊天区域 */}
        <div className="chat-container">
          {/* 会话标题栏 */}
          <div className="chat-header">
            <div className="chat-title">
              <span className="chat-title-icon">💬</span>
              <span>{sessions.find(s => s.session_id === currentSessionId)?.title || '当前会话'}</span>
            </div>
            <div className="chat-actions">
              <button className="chat-action-btn">📋 历史</button>
              <button className="chat-action-btn" onClick={handleNewSession}>🔄 新会话</button>
            </div>
          </div>

          {/* 对话历史区 */}
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-chat">
                <div className="empty-chat-icon">🤖</div>
                <div className="empty-chat-text">开始一个新的对话吧</div>
                <div className="empty-chat-subtext">输入您的问题，AI助手将为您提供专业解答</div>
              </div>
            )}
            
            {messages.map(message => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-avatar">
                  {message.type === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-bubble">
                    <div className="message-text">{message.content}</div>
                    
                    {message.type === 'ai' && (
                      <div className="message-meta">
                        <div className="message-source">
                          <span className="source-label">来源:</span>
                          <span className="source-value">{message.source}</span>
                          <span className="source-section">{message.section}</span>
                        </div>
                        <div className="message-info">
                          <span className="confidence">
                            置信度: {Math.round(message.confidence * 100)}%
                          </span>
                          {message.aiGenerated && (
                            <span className="ai-badge">AI生成</span>
                          )}
                        </div>
                        {message.confidence < 0.6 && (
                          <div className="low-confidence-warning">
                            ⚠️ 建议转人工核实
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="message-time">{message.timestamp}</div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message ai">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="message-bubble typing">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                  </div>
                  <div className="message-time">AI正在思考...</div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* 快捷问题区 */}
          <div className="quick-questions">
            <span className="quick-questions-label">快捷问题:</span>
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                className="quick-question-btn"
                onClick={() => handleQuickQuestion(question)}
              >
                {question}
              </button>
            ))}
          </div>

          {/* 输入区 */}
          <div className="chat-input-area">
            <div className="chat-input-wrapper">
              <textarea
                className="chat-input"
                placeholder="请输入您的问题..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                rows={1}
              />
              <div className="chat-input-actions">
                <button className="input-action-btn">📎</button>
                <button 
                  className="send-btn"
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isLoading}
                >
                  发送
                </button>
              </div>
            </div>
            <div className="chat-input-hint">
              按 Enter 发送，Shift + Enter 换行
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default QAChat
