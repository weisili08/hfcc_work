import { useState, useEffect } from 'react'
import { getComplaints, submitComplaint, updateComplaintStatus } from '../../../services/csApi'
import './Complaint.css'

// 模拟投诉数据
const MOCK_COMPLAINTS = [
  {
    ticket_id: 'TK-20260416-0012',
    customer_id: 'CUST****1234',
    customer_name: '张**',
    complaint_type: 'product',
    complaint_summary: '基金赎回问题，资金未到账',
    urgency: 'P1',
    status: 'processing',
    handler: { name: '李客服', id: 'agent_001' },
    created_at: '2026-04-16T08:30:00Z',
    sla_deadline: '2026-04-16T20:30:00Z',
    sla_remaining_hours: 8,
    description: '客户反映昨日提交的基金赎回申请，至今资金仍未到账，要求查询处理。'
  },
  {
    ticket_id: 'TK-20260416-0008',
    customer_id: 'CUST****5678',
    customer_name: '王**',
    complaint_type: 'service',
    complaint_summary: '客服态度问题投诉',
    urgency: 'P2',
    status: 'pending',
    handler: null,
    created_at: '2026-04-16T10:15:00Z',
    sla_deadline: '2026-04-17T10:15:00Z',
    sla_remaining_hours: 22,
    description: '客户反映昨日致电客服咨询问题时，客服人员态度冷淡，未得到满意解答。'
  },
  {
    ticket_id: 'TK-20260415-0056',
    customer_id: 'CUST****9012',
    customer_name: '刘**',
    complaint_type: 'system',
    complaint_summary: 'APP无法登录，显示系统错误',
    urgency: 'P0',
    status: 'escalated',
    handler: { name: '技术组', id: 'tech_001' },
    created_at: '2026-04-15T14:20:00Z',
    sla_deadline: '2026-04-15T18:20:00Z',
    sla_remaining_hours: -2,
    description: '客户反映手机APP从昨日下午开始无法登录，多次尝试均显示系统错误代码500。'
  },
  {
    ticket_id: 'TK-20260415-0042',
    customer_id: 'CUST****3456',
    customer_name: '陈**',
    complaint_type: 'product',
    complaint_summary: '基金净值计算疑问',
    urgency: 'P2',
    status: 'resolved',
    handler: { name: '赵客服', id: 'agent_002' },
    created_at: '2026-04-15T09:00:00Z',
    sla_deadline: '2026-04-16T09:00:00Z',
    sla_remaining_hours: 0,
    description: '客户对昨日基金净值计算结果有疑问，认为与预期不符。'
  },
  {
    ticket_id: 'TK-20260414-0031',
    customer_id: 'CUST****7890',
    customer_name: '杨**',
    complaint_type: 'staff',
    complaint_summary: '理财经理推荐不当',
    urgency: 'P1',
    status: 'closed',
    handler: { name: '主管', id: 'mgr_001' },
    created_at: '2026-04-14T16:45:00Z',
    sla_deadline: '2026-04-15T16:45:00Z',
    sla_remaining_hours: 0,
    description: '客户投诉理财经理推荐的产品与其风险承受能力不匹配，造成投资损失。'
  }
]

const typeMap = {
  product: { label: '产品', color: '#3182ce' },
  service: { label: '服务', color: '#38a169' },
  system: { label: '系统', color: '#d69e2e' },
  staff: { label: '人员', color: '#e53e3e' },
  other: { label: '其他', color: '#718096' }
}

const urgencyMap = {
  P0: { label: '紧急', color: '#ff4d4f' },
  P1: { label: '高', color: '#faad14' },
  P2: { label: '中', color: '#1890ff' },
  P3: { label: '低', color: '#52c41a' }
}

const statusMap = {
  pending: { label: '待处理', color: '#faad14' },
  processing: { label: '处理中', color: '#1890ff' },
  escalated: { label: '已升级', color: '#ff4d4f' },
  resolved: { label: '已解决', color: '#52c41a' },
  closed: { label: '已关闭', color: '#8c8c8c' }
}

function Complaint() {
  const [complaints, setComplaints] = useState(MOCK_COMPLAINTS)
  const [filteredComplaints, setFilteredComplaints] = useState(MOCK_COMPLAINTS)
  const [filterStatus, setFilterStatus] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterUrgency, setFilterUrgency] = useState('')
  const [expandedRow, setExpandedRow] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    customer_id: '',
    complaint_type: 'product',
    complaint_content: '',
    contact_phone: '',
    urgency: 'P2'
  })

  // 统计数据
  const stats = {
    pending: complaints.filter(c => c.status === 'pending').length,
    processing: complaints.filter(c => c.status === 'processing').length,
    escalated: complaints.filter(c => c.status === 'escalated').length,
    resolved: complaints.filter(c => c.status === 'resolved' || c.status === 'closed').length
  }

  // 加载投诉数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getComplaints()
        if (res?.data?.items) {
          setComplaints(res.data.items)
        }
      } catch (e) {
        console.log('Using mock complaints data')
      }
    }
    fetchData()
  }, [])

  // 筛选投诉
  useEffect(() => {
    let result = complaints
    
    if (filterStatus) {
      result = result.filter(c => c.status === filterStatus)
    }
    
    if (filterType) {
      result = result.filter(c => c.complaint_type === filterType)
    }
    
    if (filterUrgency) {
      result = result.filter(c => c.urgency === filterUrgency)
    }
    
    setFilteredComplaints(result)
  }, [complaints, filterStatus, filterType, filterUrgency])

  const handleCreateComplaint = async () => {
    try {
      const res = await submitComplaint(formData)
      
      const newComplaint = {
        ticket_id: res?.data?.ticket_id || `TK-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${String(complaints.length + 1).padStart(4,'0')}`,
        customer_id: formData.customer_id,
        customer_name: '新' + formData.customer_id.slice(-4),
        complaint_type: formData.complaint_type,
        complaint_summary: formData.complaint_content.slice(0, 30) + '...',
        urgency: formData.urgency,
        status: 'pending',
        handler: null,
        created_at: new Date().toISOString(),
        sla_deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        sla_remaining_hours: 24,
        description: formData.complaint_content
      }
      
      setComplaints([newComplaint, ...complaints])
    } catch (e) {
      console.log('Create failed, using local')
      const newComplaint = {
        ticket_id: `TK-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${String(complaints.length + 1).padStart(4,'0')}`,
        customer_id: formData.customer_id,
        customer_name: '新' + formData.customer_id.slice(-4),
        complaint_type: formData.complaint_type,
        complaint_summary: formData.complaint_content.slice(0, 30) + '...',
        urgency: formData.urgency,
        status: 'pending',
        handler: null,
        created_at: new Date().toISOString(),
        sla_deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        sla_remaining_hours: 24,
        description: formData.complaint_content
      }
      setComplaints([newComplaint, ...complaints])
    }
    
    setIsModalOpen(false)
    setFormData({
      customer_id: '',
      complaint_type: 'product',
      complaint_content: '',
      contact_phone: '',
      urgency: 'P2'
    })
  }

  const handleAction = async (ticketId, action) => {
    const statusMap = {
      assign: 'processing',
      escalate: 'escalated',
      resolve: 'resolved',
      close: 'closed'
    }
    
    try {
      await updateComplaintStatus(ticketId, { status: statusMap[action] })
    } catch (e) {
      console.log('Update failed, using local')
    }
    
    setComplaints(prev => prev.map(c => {
      if (c.ticket_id === ticketId) {
        return { ...c, status: statusMap[action] }
      }
      return c
    }))
  }

  const formatDate = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleString('zh-CN', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getSLAClass = (hours) => {
    if (hours < 0) return 'sla-overdue'
    if (hours < 4) return 'sla-warning'
    return 'sla-normal'
  }

  return (
    <div className="complaint-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">投诉管理</h1>
        <p className="page-subtitle">投诉工单创建、分配、状态跟踪、SLA管理</p>
      </div>

      {/* 统计卡片 */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(250, 173, 20, 0.1)', color: '#faad14' }}>
            ⏳
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.pending}</div>
            <div className="stat-label">待处理</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(24, 144, 255, 0.1)', color: '#1890ff' }}>
            🔧
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.processing}</div>
            <div className="stat-label">处理中</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(255, 77, 79, 0.1)', color: '#ff4d4f' }}>
            ⚠️
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.escalated}</div>
            <div className="stat-label">已升级</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(82, 196, 26, 0.1)', color: '#52c41a' }}>
            ✅
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.resolved}</div>
            <div className="stat-label">已解决</div>
          </div>
        </div>
      </div>

      {/* 筛选栏 */}
      <div className="filter-bar">
        <div className="filter-group">
          <select 
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">全部状态</option>
            <option value="pending">待处理</option>
            <option value="processing">处理中</option>
            <option value="escalated">已升级</option>
            <option value="resolved">已解决</option>
            <option value="closed">已关闭</option>
          </select>
        </div>
        <div className="filter-group">
          <select 
            className="filter-select"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">全部类型</option>
            <option value="product">产品</option>
            <option value="service">服务</option>
            <option value="system">系统</option>
            <option value="staff">人员</option>
            <option value="other">其他</option>
          </select>
        </div>
        <div className="filter-group">
          <select 
            className="filter-select"
            value={filterUrgency}
            onChange={(e) => setFilterUrgency(e.target.value)}
          >
            <option value="">全部优先级</option>
            <option value="P0">紧急</option>
            <option value="P1">高</option>
            <option value="P2">中</option>
            <option value="P3">低</option>
          </select>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setIsModalOpen(true)}
        >
          <span>+</span> 新建投诉
        </button>
      </div>

      {/* 投诉表格 */}
      <div className="complaint-table-wrapper">
        <table className="complaint-table">
          <thead>
            <tr>
              <th>工单号</th>
              <th>客户</th>
              <th>类型</th>
              <th>优先级</th>
              <th>状态</th>
              <th>处理人</th>
              <th>SLA剩余</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            {filteredComplaints.map((complaint, index) => (
              <>
                <tr 
                  key={complaint.ticket_id}
                  className={`${index % 2 === 1 ? 'even' : ''} ${expandedRow === complaint.ticket_id ? 'expanded' : ''}`}
                  onClick={() => setExpandedRow(expandedRow === complaint.ticket_id ? null : complaint.ticket_id)}
                >
                  <td className="ticket-id">{complaint.ticket_id}</td>
                  <td>
                    <div className="customer-info">
                      <span className="customer-name">{complaint.customer_name}</span>
                      <span className="customer-id">{complaint.customer_id}</span>
                    </div>
                  </td>
                  <td>
                    <span 
                      className="type-tag"
                      style={{ 
                        backgroundColor: `${typeMap[complaint.complaint_type]?.color}20`,
                        color: typeMap[complaint.complaint_type]?.color 
                      }}
                    >
                      {typeMap[complaint.complaint_type]?.label}
                    </span>
                  </td>
                  <td>
                    <span 
                      className="urgency-tag"
                      style={{ color: urgencyMap[complaint.urgency]?.color }}
                    >
                      {urgencyMap[complaint.urgency]?.label}
                    </span>
                  </td>
                  <td>
                    <span 
                      className="status-tag"
                      style={{ color: statusMap[complaint.status]?.color }}
                    >
                      {statusMap[complaint.status]?.label}
                    </span>
                  </td>
                  <td>{complaint.handler?.name || '-'}</td>
                  <td>
                    <span className={`sla-badge ${getSLAClass(complaint.sla_remaining_hours)}`}>
                      {complaint.sla_remaining_hours < 0 
                        ? `超时${Math.abs(complaint.sla_remaining_hours)}小时` 
                        : `${complaint.sla_remaining_hours}小时`}
                    </span>
                  </td>
                  <td>{formatDate(complaint.created_at)}</td>
                </tr>
                {expandedRow === complaint.ticket_id && (
                  <tr className="detail-row">
                    <td colSpan={8}>
                      <div className="complaint-detail">
                        <div className="detail-section">
                          <h4>投诉摘要</h4>
                          <p>{complaint.complaint_summary}</p>
                        </div>
                        <div className="detail-section">
                          <h4>详细描述</h4>
                          <p>{complaint.description}</p>
                        </div>
                        <div className="detail-actions">
                          {complaint.status === 'pending' && (
                            <>
                              <button 
                                className="action-btn primary"
                                onClick={() => handleAction(complaint.ticket_id, 'assign')}
                              >
                                分配处理
                              </button>
                              <button 
                                className="action-btn danger"
                                onClick={() => handleAction(complaint.ticket_id, 'escalate')}
                              >
                                升级
                              </button>
                            </>
                          )}
                          {complaint.status === 'processing' && (
                            <>
                              <button 
                                className="action-btn success"
                                onClick={() => handleAction(complaint.ticket_id, 'resolve')}
                              >
                                标记解决
                              </button>
                              <button 
                                className="action-btn danger"
                                onClick={() => handleAction(complaint.ticket_id, 'escalate')}
                              >
                                升级
                              </button>
                            </>
                          )}
                          {complaint.status === 'escalated' && (
                            <button 
                              className="action-btn success"
                              onClick={() => handleAction(complaint.ticket_id, 'resolve')}
                            >
                              标记解决
                            </button>
                          )}
                          {complaint.status === 'resolved' && (
                            <button 
                              className="action-btn secondary"
                              onClick={() => handleAction(complaint.ticket_id, 'close')}
                            >
                              关闭工单
                            </button>
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
        
        {filteredComplaints.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <div className="empty-text">暂无投诉工单</div>
          </div>
        )}
      </div>

      {/* 创建投诉弹窗 */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>新建投诉工单</h3>
              <button 
                className="modal-close"
                onClick={() => setIsModalOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-row">
                <div className="form-group">
                  <label>客户标识 *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.customer_id}
                    onChange={(e) => setFormData({...formData, customer_id: e.target.value})}
                    placeholder="请输入客户号"
                  />
                </div>
                <div className="form-group">
                  <label>联系电话</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({...formData, contact_phone: e.target.value})}
                    placeholder="请输入联系电话"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>投诉类型 *</label>
                  <select
                    className="form-select"
                    value={formData.complaint_type}
                    onChange={(e) => setFormData({...formData, complaint_type: e.target.value})}
                  >
                    <option value="product">产品</option>
                    <option value="service">服务</option>
                    <option value="system">系统</option>
                    <option value="staff">人员</option>
                    <option value="other">其他</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>紧急程度 *</label>
                  <select
                    className="form-select"
                    value={formData.urgency}
                    onChange={(e) => setFormData({...formData, urgency: e.target.value})}
                  >
                    <option value="P0">紧急</option>
                    <option value="P1">高</option>
                    <option value="P2">中</option>
                    <option value="P3">低</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>投诉内容 *</label>
                <textarea
                  className="form-textarea"
                  rows={5}
                  value={formData.complaint_content}
                  onChange={(e) => setFormData({...formData, complaint_content: e.target.value})}
                  placeholder="请详细描述投诉内容..."
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setIsModalOpen(false)}
              >
                取消
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleCreateComplaint}
                disabled={!formData.customer_id || !formData.complaint_content}
              >
                提交
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Complaint
