import { useState, useEffect } from 'react'
import { getKnowledge, updateKnowledge, deleteKnowledge, createKnowledge } from '../../../services/csApi'
import './Knowledge.css'

// 模拟知识库数据
const MOCK_KNOWLEDGE_BASES = [
  {
    kb_id: 'kb_001',
    name: '产品知识库',
    description: '基金产品相关信息',
    doc_count: 156,
    status: 'active'
  },
  {
    kb_id: 'kb_002',
    name: '业务规则库',
    description: '业务流程与规则说明',
    doc_count: 89,
    status: 'active'
  },
  {
    kb_id: 'kb_003',
    name: '操作手册库',
    description: '系统操作指南',
    doc_count: 45,
    status: 'active'
  }
]

// 模拟文档数据
const MOCK_DOCUMENTS = [
  {
    doc_id: 'doc_001',
    kb_id: 'kb_001',
    title: 'XX稳健增长混合基金产品说明',
    category: 'product',
    status: 'active',
    created_at: '2026-01-15T10:00:00Z',
    updated_at: '2026-04-10T14:30:00Z'
  },
  {
    doc_id: 'doc_002',
    kb_id: 'kb_001',
    title: '货币基金申购赎回规则',
    category: 'rule',
    status: 'active',
    created_at: '2026-02-20T09:00:00Z',
    updated_at: '2026-03-15T11:20:00Z'
  },
  {
    doc_id: 'doc_003',
    kb_id: 'kb_001',
    title: '基金定投业务操作指南',
    category: 'process',
    status: 'inactive',
    created_at: '2026-01-10T08:00:00Z',
    updated_at: '2026-02-28T16:45:00Z'
  },
  {
    doc_id: 'doc_004',
    kb_id: 'kb_002',
    title: '客户风险评估流程',
    category: 'process',
    status: 'active',
    created_at: '2026-03-01T10:00:00Z',
    updated_at: '2026-04-05T09:30:00Z'
  },
  {
    doc_id: 'doc_005',
    kb_id: 'kb_002',
    title: '反洗钱合规检查要点',
    category: 'rule',
    status: 'active',
    created_at: '2026-02-15T14:00:00Z',
    updated_at: '2026-03-20T10:15:00Z'
  }
]

const categoryMap = {
  product: { label: '产品', color: '#3182ce' },
  rule: { label: '规则', color: '#38a169' },
  process: { label: '流程', color: '#d69e2e' },
  system: { label: '系统', color: '#805ad5' }
}

const statusMap = {
  active: { label: '已发布', color: '#52c41a' },
  inactive: { label: '草稿', color: '#faad14' },
  archived: { label: '已归档', color: '#8c8c8c' }
}

function Knowledge() {
  const [knowledgeBases, setKnowledgeBases] = useState(MOCK_KNOWLEDGE_BASES)
  const [selectedKb, setSelectedKb] = useState(null)
  const [documents, setDocuments] = useState(MOCK_DOCUMENTS)
  const [filteredDocs, setFilteredDocs] = useState(MOCK_DOCUMENTS)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDoc, setEditingDoc] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    category: 'product',
    status: 'active',
    content: ''
  })

  // 加载知识库数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getKnowledge()
        if (res?.data?.items) {
          // 这里假设API返回的是文档列表
          console.log('Loaded knowledge data:', res.data)
        }
      } catch (e) {
        console.log('Using mock knowledge data')
      }
    }
    fetchData()
  }, [])

  // 筛选文档
  useEffect(() => {
    let result = documents
    
    if (selectedKb) {
      result = result.filter(d => d.kb_id === selectedKb.kb_id)
    }
    
    if (searchKeyword) {
      result = result.filter(d => 
        d.title.toLowerCase().includes(searchKeyword.toLowerCase())
      )
    }
    
    if (filterCategory) {
      result = result.filter(d => d.category === filterCategory)
    }
    
    if (filterStatus) {
      result = result.filter(d => d.status === filterStatus)
    }
    
    setFilteredDocs(result)
  }, [documents, selectedKb, searchKeyword, filterCategory, filterStatus])

  const handleCreateDoc = () => {
    setEditingDoc(null)
    setFormData({
      title: '',
      category: 'product',
      status: 'active',
      content: ''
    })
    setIsModalOpen(true)
  }

  const handleEditDoc = (doc) => {
    setEditingDoc(doc)
    setFormData({
      title: doc.title,
      category: doc.category,
      status: doc.status,
      content: '文档内容...' // 实际应从API获取完整内容
    })
    setIsModalOpen(true)
  }

  const handleSaveDoc = async () => {
    try {
      if (editingDoc) {
        // 更新文档
        await updateKnowledge({
          kb_id: editingDoc.doc_id,
          ...formData
        })
        
        setDocuments(prev => prev.map(d => 
          d.doc_id === editingDoc.doc_id 
            ? { ...d, ...formData, updated_at: new Date().toISOString() }
            : d
        ))
      } else {
        // 创建新文档
        const res = await createKnowledge({
          ...formData,
          kb_id: selectedKb?.kb_id || 'kb_001'
        })
        
        const newDoc = {
          doc_id: res?.data?.kb_id || `doc_${Date.now()}`,
          kb_id: selectedKb?.kb_id || 'kb_001',
          ...formData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        setDocuments([newDoc, ...documents])
      }
    } catch (e) {
      console.log('Save failed, using local update')
      // 本地更新
      if (editingDoc) {
        setDocuments(prev => prev.map(d => 
          d.doc_id === editingDoc.doc_id 
            ? { ...d, ...formData, updated_at: new Date().toISOString() }
            : d
        ))
      } else {
        const newDoc = {
          doc_id: `doc_${Date.now()}`,
          kb_id: selectedKb?.kb_id || 'kb_001',
          ...formData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        setDocuments([newDoc, ...documents])
      }
    }
    
    setIsModalOpen(false)
  }

  const handleDeleteDoc = async (docId) => {
    if (!window.confirm('确定要删除该文档吗？')) return
    
    try {
      await deleteKnowledge(docId)
    } catch (e) {
      console.log('Delete failed, removing locally')
    }
    
    setDocuments(prev => prev.filter(d => d.doc_id !== docId))
  }

  const formatDate = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleDateString('zh-CN')
  }

  return (
    <div className="knowledge-page">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">知识库管理</h1>
        <p className="page-subtitle">知识条目管理与维护</p>
      </div>

      {/* 知识库列表 */}
      {!selectedKb && (
        <div className="kb-list-section">
          <div className="section-header">
            <h2 className="section-title">知识库列表</h2>
            <button className="btn btn-primary">
              <span>+</span> 新建知识库
            </button>
          </div>
          
          <div className="kb-grid">
            {knowledgeBases.map(kb => (
              <div 
                key={kb.kb_id} 
                className="kb-card"
                onClick={() => setSelectedKb(kb)}
              >
                <div className="kb-card-header">
                  <div className="kb-icon">📚</div>
                  <span 
                    className="kb-status"
                    style={{ color: statusMap[kb.status]?.color }}
                  >
                    {statusMap[kb.status]?.label}
                  </span>
                </div>
                <h3 className="kb-name">{kb.name}</h3>
                <p className="kb-description">{kb.description}</p>
                <div className="kb-stats">
                  <span className="kb-doc-count">
                    <strong>{kb.doc_count}</strong> 篇文档
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 文档列表 */}
      {selectedKb && (
        <div className="doc-list-section">
          <div className="section-header">
            <div className="section-title-row">
              <button 
                className="back-btn"
                onClick={() => setSelectedKb(null)}
              >
                ← 返回
              </button>
              <h2 className="section-title">{selectedKb.name}</h2>
            </div>
            <button className="btn btn-primary" onClick={handleCreateDoc}>
              <span>+</span> 新建文档
            </button>
          </div>

          {/* 筛选栏 */}
          <div className="filter-bar">
            <div className="filter-group">
              <input
                type="text"
                className="filter-input"
                placeholder="搜索文档..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <select 
                className="filter-select"
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <option value="">全部分类</option>
                <option value="product">产品</option>
                <option value="rule">规则</option>
                <option value="process">流程</option>
                <option value="system">系统</option>
              </select>
            </div>
            <div className="filter-group">
              <select 
                className="filter-select"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="">全部状态</option>
                <option value="active">已发布</option>
                <option value="inactive">草稿</option>
                <option value="archived">已归档</option>
              </select>
            </div>
          </div>

          {/* 文档表格 */}
          <div className="doc-table-wrapper">
            <table className="doc-table">
              <thead>
                <tr>
                  <th>标题</th>
                  <th>分类</th>
                  <th>状态</th>
                  <th>创建时间</th>
                  <th>更新时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc, index) => (
                  <tr key={doc.doc_id} className={index % 2 === 1 ? 'even' : ''}>
                    <td className="doc-title-cell">
                      <span className="doc-icon">📄</span>
                      {doc.title}
                    </td>
                    <td>
                      <span 
                        className="category-tag"
                        style={{ 
                          backgroundColor: `${categoryMap[doc.category]?.color}20`,
                          color: categoryMap[doc.category]?.color 
                        }}
                      >
                        {categoryMap[doc.category]?.label}
                      </span>
                    </td>
                    <td>
                      <span 
                        className="status-tag"
                        style={{ color: statusMap[doc.status]?.color }}
                      >
                        {statusMap[doc.status]?.label}
                      </span>
                    </td>
                    <td>{formatDate(doc.created_at)}</td>
                    <td>{formatDate(doc.updated_at)}</td>
                    <td>
                      <div className="action-btns">
                        <button 
                          className="action-btn edit"
                          onClick={() => handleEditDoc(doc)}
                          title="编辑"
                        >
                          ✏️
                        </button>
                        <button 
                          className="action-btn delete"
                          onClick={() => handleDeleteDoc(doc.doc_id)}
                          title="删除"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredDocs.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <div className="empty-text">暂无文档</div>
                <div className="empty-subtext">点击"新建文档"按钮创建第一篇文档</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 创建/编辑弹窗 */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingDoc ? '编辑文档' : '新建文档'}</h3>
              <button 
                className="modal-close"
                onClick={() => setIsModalOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>文档标题</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="请输入文档标题"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>分类</label>
                  <select
                    className="form-select"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    <option value="product">产品</option>
                    <option value="rule">规则</option>
                    <option value="process">流程</option>
                    <option value="system">系统</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>状态</label>
                  <select
                    className="form-select"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <option value="active">已发布</option>
                    <option value="inactive">草稿</option>
                    <option value="archived">已归档</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>文档内容</label>
                <textarea
                  className="form-textarea"
                  rows={8}
                  value={formData.content}
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  placeholder="请输入文档内容..."
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
                onClick={handleSaveDoc}
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Knowledge
