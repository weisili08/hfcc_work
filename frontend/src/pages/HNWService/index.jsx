import { useState, useEffect } from 'react'
import { getAllocationAdvice, generateCarePlan, generateEventPlan, getTouchpoints } from '../../services/hnwApi'
import './HNWService.css'

// Tab配置
const TABS = [
  { key: 'customers', label: '客户列表', icon: '👥' },
  { key: 'allocation', label: '资产配置', icon: '📊' },
  { key: 'care', label: '客户关怀', icon: '💝' },
  { key: 'events', label: '活动管理', icon: '🎉' }
]

// 模拟客户数据
const MOCK_CUSTOMERS = [
  {
    customer_id: 'HNW001',
    name: '张**',
    level: '钻石',
    aum: 2850,
    risk_level: 'C4',
    tags: ['高净值', '活跃交易', '偏好固收'],
    last_contact: '2026-04-10'
  },
  {
    customer_id: 'HNW002',
    name: '李**',
    level: '白金',
    aum: 1680,
    risk_level: 'C3',
    tags: ['稳健型', '长期持有'],
    last_contact: '2026-04-08'
  },
  {
    customer_id: 'HNW003',
    name: '王**',
    level: '钻石',
    aum: 5200,
    risk_level: 'C5',
    tags: ['超高净值', '股权投资', '海外配置'],
    last_contact: '2026-04-12'
  },
  {
    customer_id: 'HNW004',
    name: '陈**',
    level: '白金',
    aum: 1250,
    risk_level: 'C2',
    tags: ['保守型', '定期理财'],
    last_contact: '2026-04-05'
  },
  {
    customer_id: 'HNW005',
    name: '刘**',
    level: '黄金',
    aum: 680,
    risk_level: 'C3',
    tags: ['成长型', '基金定投'],
    last_contact: '2026-04-14'
  }
]

// 模拟资产配置建议
const MOCK_ALLOCATION = {
  advice_id: 'alloc_001',
  customer_portrait: {
    risk_profile: '稳健型投资者',
    investment_style: '追求长期稳定收益，可承受适度波动'
  },
  current_analysis: {
    total_aum: 2850,
    allocation: [
      { asset_class: '货币基金', percentage: 35, amount: 997.5 },
      { asset_class: '债券基金', percentage: 40, amount: 1140 },
      { asset_class: '混合基金', percentage: 20, amount: 570 },
      { asset_class: '股票基金', percentage: 5, amount: 142.5 }
    ]
  },
  recommendations: {
    target_allocation: [
      { asset_class: '货币基金', percentage: 20, products: ['XX货币基金', 'YY活期理财'] },
      { asset_class: '债券基金', percentage: 35, products: ['XX纯债基金', 'YY信用债基'] },
      { asset_class: '混合基金', percentage: 30, products: ['XX稳健混合', 'YY灵活配置'] },
      { asset_class: '股票基金', percentage: 15, products: ['XX沪深300', 'YY中证500'] }
    ],
    adjustment_reason: '根据当前市场环境及您的风险偏好，建议适当增加权益类资产配置，以提升长期收益潜力。同时保持足够的流动性储备。'
  },
  risk_warning: '以上配置建议仅供参考，投资有风险，入市需谨慎。',
  disclaimer: '本建议由AI生成，不构成投资建议。'
}

// 模拟关怀任务
const MOCK_CARE_TASKS = [
  {
    task_id: 'care_001',
    customer_name: '张**',
    touchpoint_type: 'birthday',
    event_date: '2026-04-20',
    days_until: 4,
    status: 'pending',
    suggested_action: '生日祝福及专属礼品推荐'
  },
  {
    task_id: 'care_002',
    customer_name: '李**',
    touchpoint_type: 'anniversary',
    event_date: '2026-04-25',
    days_until: 9,
    status: 'pending',
    suggested_action: '投资周年回顾及组合优化建议'
  },
  {
    task_id: 'care_003',
    customer_name: '王**',
    touchpoint_type: 'market_volatility',
    event_date: '2026-04-16',
    days_until: 0,
    status: 'urgent',
    suggested_action: '市场波动关怀，安抚情绪'
  }
]

// 模拟活动数据
const MOCK_EVENTS = [
  {
    event_id: 'evt_001',
    title: '2026年春季投资策略会',
    type: 'fixed_income',
    date: '2026-04-28',
    location: '北京金融街中心',
    attendees: 45,
    status: 'upcoming'
  },
  {
    event_id: 'evt_002',
    title: '高端客户答谢晚宴',
    type: 'client_appreciation',
    date: '2026-05-15',
    location: '国贸大酒店',
    attendees: 80,
    status: 'planning'
  }
]

const levelMap = {
  '钻石': { color: '#722ed1', bg: '#f9f0ff' },
  '白金': { color: '#1890ff', bg: '#e6f7ff' },
  '黄金': { color: '#faad14', bg: '#fffbe6' }
}

const riskMap = {
  'C1': '保守型',
  'C2': '稳健型',
  'C3': '平衡型',
  'C4': '成长型',
  'C5': '进取型'
}

function HNWService() {
  const [activeTab, setActiveTab] = useState('customers')
  const [customers, setCustomers] = useState(MOCK_CUSTOMERS)
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [allocationResult, setAllocationResult] = useState(null)
  const [isGeneratingAllocation, setIsGeneratingAllocation] = useState(false)
  const [careTasks, setCareTasks] = useState(MOCK_CARE_TASKS)
  const [generatedPlan, setGeneratedPlan] = useState(null)
  const [events, setEvents] = useState(MOCK_EVENTS)
  const [generatedEvent, setGeneratedEvent] = useState(null)

  // 加载数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getTouchpoints()
        if (res?.data?.items) {
          // 处理关怀任务数据
        }
      } catch (e) {
        console.log('Using mock data')
      }
    }
    fetchData()
  }, [])

  // 生成资产配置建议
  const handleGenerateAllocation = async () => {
    if (!selectedCustomer) {
      alert('请先选择客户')
      return
    }

    setIsGeneratingAllocation(true)
    try {
      const res = await getAllocationAdvice({
        customer_id: selectedCustomer.customer_id,
        risk_level: selectedCustomer.risk_level,
        aum_range: `${selectedCustomer.aum}万`,
        investment_goal: '稳健增值'
      })
      if (res?.data) {
        setAllocationResult(res.data)
      }
    } catch (e) {
      console.log('Using mock allocation')
      setAllocationResult({
        ...MOCK_ALLOCATION,
        current_analysis: {
          ...MOCK_ALLOCATION.current_analysis,
          total_aum: selectedCustomer.aum
        }
      })
    } finally {
      setIsGeneratingAllocation(false)
    }
  }

  // 生成关怀计划
  const handleGenerateCarePlan = async (task) => {
    try {
      const res = await generateCarePlan({
        customer_id: task.customer_id,
        touchpoint_type: task.touchpoint_type
      })
      if (res?.data) {
        setGeneratedPlan(res.data)
      }
    } catch (e) {
      console.log('Using mock care plan')
      setGeneratedPlan({
        plan_id: 'plan_001',
        touchpoint_type: task.touchpoint_type,
        care_plan: {
          suggested_channel: '电话+微信',
          suggested_timing: '上午10:00-11:00',
          key_messages: [
            '诚挚的生日祝福',
            '回顾一年来的投资成果',
            '介绍专属生日礼遇'
          ],
          script_template: '张先生您好，我是您的专属理财顾问小李。首先祝您生日快乐！...',
          accompanying_services: ['专属礼品', '费率优惠']
        }
      })
    }
  }

  // 生成活动策划
  const handleGenerateEvent = async () => {
    try {
      const res = await generateEventPlan({
        event_type: 'client_appreciation',
        target_audience: '高净值客户',
        expected_attendees: 50
      })
      if (res?.data) {
        setGeneratedEvent(res.data)
      }
    } catch (e) {
      console.log('Using mock event plan')
      setGeneratedEvent({
        plan_id: 'event_001',
        event_proposal: {
          theme: '财富传承与家族信托专题沙龙',
          date_suggestion: '2026年5月20日 14:00-17:00',
          venue_suggestion: '金融街威斯汀酒店 宴会厅',
          agenda: [
            { time: '14:00-14:30', activity: '签到及茶歇', duration: 30 },
            { time: '14:30-15:30', activity: '家族信托法律架构解析', duration: 60 },
            { time: '15:30-15:45', activity: '茶歇', duration: 15 },
            { time: '15:45-16:45', activity: '财富传承案例分享', duration: 60 },
            { time: '16:45-17:00', activity: '互动交流', duration: 15 }
          ],
          materials_checklist: ['邀请函', '签到表', '资料袋', '茶歇'],
          budget_estimate: { total: 50000, per_person: 1000 }
        }
      })
    }
  }

  // 渲染客户列表Tab
  const renderCustomersTab = () => (
    <div className="tab-content">
      <div className="customers-grid">
        {customers.map(customer => (
          <div 
            key={customer.customer_id} 
            className="customer-card"
            onClick={() => setSelectedCustomer(customer)}
          >
            <div className="customer-header">
              <div className="customer-avatar">
                {customer.name.charAt(0)}
              </div>
              <div className="customer-info">
                <h4>{customer.name}</h4>
                <span 
                  className="level-badge"
                  style={{ 
                    backgroundColor: levelMap[customer.level]?.bg,
                    color: levelMap[customer.level]?.color 
                  }}
                >
                  {customer.level}
                </span>
              </div>
            </div>
            <div className="customer-stats">
              <div className="stat">
                <span className="stat-label">AUM</span>
                <span className="stat-value">{customer.aum}万</span>
              </div>
              <div className="stat">
                <span className="stat-label">风险偏好</span>
                <span className="stat-value">{riskMap[customer.risk_level]}</span>
              </div>
            </div>
            <div className="customer-tags">
              {customer.tags.map((tag, idx) => (
                <span key={idx} className="tag">{tag}</span>
              ))}
            </div>
            <div className="customer-footer">
              <span>最近联系: {customer.last_contact}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  // 渲染资产配置Tab
  const renderAllocationTab = () => (
    <div className="tab-content">
      <div className="allocation-panel">
        <div className="panel-section">
          <h3>选择客户</h3>
          <div className="customer-selector">
            {customers.map(c => (
              <button
                key={c.customer_id}
                className={`selector-btn ${selectedCustomer?.customer_id === c.customer_id ? 'active' : ''}`}
                onClick={() => setSelectedCustomer(c)}
              >
                {c.name} ({c.aum}万)
              </button>
            ))}
          </div>
          <button 
            className="generate-btn"
            onClick={handleGenerateAllocation}
            disabled={isGeneratingAllocation || !selectedCustomer}
          >
            {isGeneratingAllocation ? 'AI生成中...' : '🤖 生成AI配置建议'}
          </button>
        </div>

        {allocationResult && (
          <div className="allocation-result">
            <div className="result-header">
              <h3>资产配置建议</h3>
              <span className="aum-total">总资产: {allocationResult.current_analysis.total_aum}万</span>
            </div>
            
            {/* 配置饼图 */}
            <div className="allocation-chart">
              <div className="pie-chart">
                {allocationResult.recommendations.target_allocation.map((item, idx) => {
                  const colors = ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5']
                  return (
                    <div 
                      key={idx}
                      className="pie-segment"
                      style={{
                        backgroundColor: colors[idx % colors.length],
                        flex: item.percentage
                      }}
                      title={`${item.asset_class}: ${item.percentage}%`}
                    >
                      <span>{item.percentage}%</span>
                    </div>
                  )
                })}
              </div>
              <div className="pie-legend">
                {allocationResult.recommendations.target_allocation.map((item, idx) => {
                  const colors = ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5']
                  return (
                    <div key={idx} className="legend-item">
                      <span 
                        className="legend-color"
                        style={{ backgroundColor: colors[idx % colors.length] }}
                      />
                      <span className="legend-label">{item.asset_class}</span>
                      <span className="legend-value">{item.percentage}%</span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 推荐产品 */}
            <div className="recommended-products">
              <h4>推荐产品</h4>
              {allocationResult.recommendations.target_allocation.map((item, idx) => (
                <div key={idx} className="product-group">
                  <h5>{item.asset_class} ({item.percentage}%)</h5>
                  <div className="product-list">
                    {item.products?.map((product, pidx) => (
                      <span key={pidx} className="product-tag">{product}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="allocation-reason">
              <h4>调整理由</h4>
              <p>{allocationResult.recommendations.adjustment_reason}</p>
            </div>

            <div className="risk-warning">
              ⚠️ {allocationResult.risk_warning}
            </div>
          </div>
        )}
      </div>
    </div>
  )

  // 渲染客户关怀Tab
  const renderCareTab = () => (
    <div className="tab-content">
      <div className="care-panel">
        <div className="care-tasks">
          <h3>关怀任务列表</h3>
          {careTasks.map(task => (
            <div 
              key={task.task_id} 
              className={`care-task ${task.status}`}
              onClick={() => handleGenerateCarePlan(task)}
            >
              <div className="task-header">
                <span className="customer-name">{task.customer_name}</span>
                <span className={`task-status ${task.status}`}>
                  {task.status === 'urgent' ? '紧急' : task.days_until === 0 ? '今天' : `${task.days_until}天后`}
                </span>
              </div>
              <div className="task-type">
                {task.touchpoint_type === 'birthday' && '🎂 生日关怀'}
                {task.touchpoint_type === 'anniversary' && '📅 投资周年'}
                {task.touchpoint_type === 'market_volatility' && '📉 市场波动'}
              </div>
              <div className="task-action">{task.suggested_action}</div>
            </div>
          ))}
        </div>

        {generatedPlan && (
          <div className="care-plan-result">
            <h3>💝 关怀计划</h3>
            <div className="plan-section">
              <h4>建议渠道</h4>
              <p>{generatedPlan.care_plan.suggested_channel}</p>
            </div>
            <div className="plan-section">
              <h4>建议时机</h4>
              <p>{generatedPlan.care_plan.suggested_timing}</p>
            </div>
            <div className="plan-section">
              <h4>关键信息点</h4>
              <ul>
                {generatedPlan.care_plan.key_messages.map((msg, idx) => (
                  <li key={idx}>{msg}</li>
                ))}
              </ul>
            </div>
            <div className="plan-section">
              <h4>话术模板</h4>
              <div className="script-box">{generatedPlan.care_plan.script_template}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  // 渲染活动管理Tab
  const renderEventsTab = () => (
    <div className="tab-content">
      <div className="events-panel">
        <div className="events-header">
          <h3>活动列表</h3>
          <button className="generate-btn" onClick={handleGenerateEvent}>
            ✨ AI策划活动
          </button>
        </div>
        
        <div className="events-list">
          {events.map(event => (
            <div key={event.event_id} className="event-card">
              <div className="event-date">
                <span className="month">{event.date.slice(5, 7)}月</span>
                <span className="day">{event.date.slice(8)}</span>
              </div>
              <div className="event-info">
                <h4>{event.title}</h4>
                <p>📍 {event.location}</p>
                <p>👥 {event.attendees}人参与</p>
              </div>
              <span className={`event-status ${event.status}`}>
                {event.status === 'upcoming' ? '即将开始' : '筹备中'}
              </span>
            </div>
          ))}
        </div>

        {generatedEvent && (
          <div className="generated-event">
            <h3>🎉 AI策划方案</h3>
            <h4>{generatedEvent.event_proposal.theme}</h4>
            <p>📅 {generatedEvent.event_proposal.date_suggestion}</p>
            <p>📍 {generatedEvent.event_proposal.venue_suggestion}</p>
            
            <h5>活动流程</h5>
            <div className="agenda-list">
              {generatedEvent.event_proposal.agenda.map((item, idx) => (
                <div key={idx} className="agenda-item">
                  <span className="time">{item.time}</span>
                  <span className="activity">{item.activity}</span>
                  <span className="duration">{item.duration}分钟</span>
                </div>
              ))}
            </div>
            
            <div className="budget-info">
              <span>预算: ¥{generatedEvent.event_proposal.budget_estimate.total.toLocaleString()}</span>
              <span>人均: ¥{generatedEvent.event_proposal.budget_estimate.per_person}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <div className="hnw-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">高净值客户服务</h1>
        <p className="page-subtitle">客户视图整合、资产配置建议、客户关怀引擎、活动策划执行</p>
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
      {activeTab === 'customers' && renderCustomersTab()}
      {activeTab === 'allocation' && renderAllocationTab()}
      {activeTab === 'care' && renderCareTab()}
      {activeTab === 'events' && renderEventsTab()}
    </div>
  )
}

export default HNWService
