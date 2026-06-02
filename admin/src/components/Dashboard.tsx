import React, { useEffect, useState } from 'react';
import { getDialogStats, getDialogs, getKnowledge, logout, createKnowledge, updateKnowledge, deleteKnowledge } from '../api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({ total: 0, bot_answered: 0, expert_answered: 0, pending: 0 });
  const [recentDialogs, setRecentDialogs] = useState<any[]>([]);
  const [knowledgeList, setKnowledgeList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState<'dialogs' | 'knowledge'>('dialogs');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formData, setFormData] = useState({ question: '', answer: '', category: 'general' });
  const [dialogPage, setDialogPage] = useState(1);
  const [dialogTotal, setDialogTotal] = useState(0);
  const [filterUserId, setFilterUserId] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [knowledgeSearch, setKnowledgeSearch] = useState('');
  const [knowledgePage, setKnowledgePage] = useState(1);
  const [knowledgeTotal, setKnowledgeTotal] = useState(0);

  useEffect(() => {
    fetchData();
  }, [dialogPage, filterUserId, filterSource, dateFrom, dateTo, knowledgePage, knowledgeSearch]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, dialogsRes, knowledgeRes] = await Promise.all([
        getDialogStats(),
        getDialogs(dialogPage, 20, filterUserId ? parseInt(filterUserId) : undefined, filterSource || undefined),
        getKnowledge(knowledgePage, 20, knowledgeSearch || undefined)
      ]);
      setStats(statsRes.data);
      setRecentDialogs(dialogsRes.data.data);
      setDialogTotal(dialogsRes.data.total);
      setKnowledgeList(knowledgeRes.data.data);
      setKnowledgeTotal(knowledgeRes.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    window.location.reload();
  };

  const toggleTheme = () => setDarkMode(!darkMode);

  const handleCreate = async () => {
    if (!formData.question || !formData.answer) return;
    try {
      await createKnowledge(formData);
      setShowAddForm(false);
      setFormData({ question: '', answer: '', category: 'general' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdate = async () => {
    if (!editingItem) return;
    try {
      await updateKnowledge(editingItem.id, formData);
      setEditingItem(null);
      setFormData({ question: '', answer: '', category: 'general' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить этот вопрос?')) {
      try {
        await deleteKnowledge(id);
        fetchData();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const startEdit = (item: any) => {
    setEditingItem(item);
    setFormData({ question: item.question, answer: item.answer, category: item.category || 'general' });
  };

  const cancelForm = () => {
    setShowAddForm(false);
    setEditingItem(null);
    setFormData({ question: '', answer: '', category: 'general' });
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Пользователь', 'Вопрос', 'Ответ', 'Источник', 'Дата'];
    const rows = recentDialogs.map(d => [
      d.id, d.user_name || d.user_id, d.user_question, d.final_answer || '', d.source, new Date(d.asked_at).toLocaleString()
    ]);
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `dialogs_${new Date().toISOString().slice(0, 19)}.csv`;
    link.click();
  };

  const resetFilters = () => {
    setFilterUserId('');
    setFilterSource('');
    setDateFrom('');
    setDateTo('');
    setDialogPage(1);
  };

  const theme = {
    bg: darkMode ? '#0a0c10' : '#f8f9fc',
    sidebar: darkMode ? '#0d1117' : '#ffffff',
    card: darkMode ? '#161b22' : '#ffffff',
    text: darkMode ? '#e6edf3' : '#1f2937',
    textSecondary: darkMode ? '#8b949e' : '#6b7280',
    border: darkMode ? '#30363d' : '#e5e7eb',
    accent: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
  };

  if (loading) return <div style={{ padding: '20px', color: theme.text, background: theme.bg, minHeight: '100vh' }}>Загрузка...</div>;

  const getSourceIcon = (source: string) => {
    switch(source) {
      case 'bot_qwen': return '🤖';
      case 'expert': return '👨‍🏫';
      case 'pending_expert': return '⏳';
      default: return '📝';
    }
  };

  const getSourceColor = (source: string) => {
    switch(source) {
      case 'bot_qwen': return '#3b82f6';
      case 'expert': return '#10b981';
      case 'pending_expert': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const totalAnswers = stats.bot_answered + stats.expert_answered;
  const botPercent = totalAnswers ? (stats.bot_answered / totalAnswers * 100).toFixed(1) : 0;
  const expertPercent = totalAnswers ? (stats.expert_answered / totalAnswers * 100).toFixed(1) : 0;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: theme.bg, height: '100vh', overflow: 'hidden' }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-fade { animation: fadeIn 0.3s ease-out; }
        .animate-slide { animation: slideIn 0.3s ease-out; }
        button, .card { transition: all 0.2s ease-in-out; }
        button:hover { transform: translateY(-1px); opacity: 0.9; }
      `}</style>

      {/* Sidebar */}
      <div style={{ width: '260px', background: theme.sidebar, borderRight: `1px solid ${theme.border}`, padding: '20px 16px', display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto' }}>
        <div style={{ marginBottom: '28px' }}>
          <h1 style={{ fontSize: '18px', marginBottom: '4px', color: theme.text }}>🤖 ExpertBot</h1>
          <p style={{ fontSize: '11px', color: theme.textSecondary }}>Админ-панель</p>
        </div>
        <nav style={{ flex: 1 }}>
          <button onClick={() => setActiveTab('dialogs')} style={{ width: '100%', padding: '10px 14px', marginBottom: '6px', background: activeTab === 'dialogs' ? theme.accent : 'transparent', color: activeTab === 'dialogs' ? 'white' : theme.text, border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '13px', fontWeight: 500 }}>
            💬 Диалоги
          </button>
          <button onClick={() => setActiveTab('knowledge')} style={{ width: '100%', padding: '10px 14px', marginBottom: '6px', background: activeTab === 'knowledge' ? theme.accent : 'transparent', color: activeTab === 'knowledge' ? 'white' : theme.text, border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '13px', fontWeight: 500 }}>
            📚 База знаний
          </button>
        </nav>
        <div style={{ marginTop: 'auto', paddingTop: '20px', paddingBottom: '35px', borderTop: `1px solid ${theme.border}` }}>
          <button onClick={toggleTheme} style={{ width: '100%', padding: '8px', background: 'transparent', color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px', cursor: 'pointer', marginBottom: '10px', fontSize: '13px' }}>
            {darkMode ? '☀️ Светлая' : '🌙 Тёмная'}
          </button>
          <button onClick={handleLogout} style={{ width: '100%', padding: '8px', background: 'transparent', color: theme.danger, border: `1px solid ${theme.danger}`, borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }}>
            🚪 Выйти
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        {/* Stats Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div className="card" style={{ background: theme.card, borderRadius: '12px', padding: '16px', border: `1px solid ${theme.border}` }}>
            <div style={{ fontSize: '12px', color: theme.textSecondary }}>Всего диалогов</div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: theme.text }}>{stats.total}</div>
          </div>
          <div className="card" style={{ background: theme.card, borderRadius: '12px', padding: '16px', border: `1px solid ${theme.border}` }}>
            <div style={{ fontSize: '12px', color: theme.textSecondary }}>🤖 Бот ответил</div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: theme.success }}>{stats.bot_answered}</div>
          </div>
          <div className="card" style={{ background: theme.card, borderRadius: '12px', padding: '16px', border: `1px solid ${theme.border}` }}>
            <div style={{ fontSize: '12px', color: theme.textSecondary }}>👨‍🏫 Эксперт ответил</div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: theme.warning }}>{stats.expert_answered}</div>
          </div>
          <div className="card" style={{ background: theme.card, borderRadius: '12px', padding: '16px', border: `1px solid ${theme.border}` }}>
            <div style={{ fontSize: '12px', color: theme.textSecondary }}>⏳ В ожидании</div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: theme.accent }}>{stats.pending}</div>
          </div>
        </div>

        {/* График */}
        <div className="animate-fade" style={{ background: theme.card, borderRadius: '12px', border: `1px solid ${theme.border}`, padding: '20px', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '16px', color: theme.text }}>📊 Распределение ответов</h3>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, height: '30px', background: darkMode ? '#1e1e1e' : '#e5e7eb', borderRadius: '8px', overflow: 'hidden', display: 'flex' }}>
              <div style={{ width: `${botPercent}%`, background: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '12px', fontWeight: 'bold' }}>🤖 {botPercent}%</div>
              <div style={{ width: `${expertPercent}%`, background: '#f59e0b', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '12px', fontWeight: 'bold' }}>👨‍🏫 {expertPercent}%</div>
            </div>
            <div style={{ display: 'flex', gap: '16px' }}>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', background: '#10b981', borderRadius: '2px', marginRight: '6px' }}></span>Бот</div>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', background: '#f59e0b', borderRadius: '2px', marginRight: '6px' }}></span>Эксперт</div>
            </div>
          </div>
        </div>
        {activeTab === 'dialogs' && (
          <div className="animate-fade" style={{ background: theme.card, borderRadius: '12px', border: `1px solid ${theme.border}`, overflow: 'hidden' }}>
            <div style={{ padding: '20px', borderBottom: `1px solid ${theme.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: theme.text }}>💬 Диалоги</h2>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button onClick={exportToCSV} style={{ padding: '6px 12px', background: theme.success, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>📎 Экспорт CSV</button>
                <button onClick={resetFilters} style={{ padding: '6px 12px', background: theme.warning, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>🔄 Сброс</button>
              </div>
            </div>
            
            {/* Фильтры */}
            <div style={{ padding: '16px', borderBottom: `1px solid ${theme.border}`, display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <input type="number" placeholder="User ID" value={filterUserId} onChange={(e) => setFilterUserId(e.target.value)} style={{ padding: '8px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px', fontSize: '13px', width: '120px' }} />
              <select value={filterSource} onChange={(e) => setFilterSource(e.target.value)} style={{ padding: '8px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px', fontSize: '13px' }}>
                <option value="">Все источники</option>
                <option value="bot_qwen">🤖 Бот</option>
                <option value="expert">👨‍🏫 Эксперт</option>
                <option value="pending_expert">⏳ Ожидает</option>
              </select>
              <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} style={{ padding: '8px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px', fontSize: '13px' }} />
              <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} style={{ padding: '8px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px', fontSize: '13px' }} />
            </div>

                        {/* Таблица диалогов */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: darkMode ? '#0d1117' : '#f9fafb' }}>
                    <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>ID</th>
                    <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Пользователь</th>
                    <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Вопрос</th>
                    <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Источник</th>
                    <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Дата</th>
                  </tr>
                </thead>
                <tbody>
                  {recentDialogs.map((dialog) => (
                    <tr key={dialog.id} style={{ borderTop: `1px solid ${theme.border}` }}>
                      <td style={{ padding: '10px 12px', fontSize: '12px', color: theme.textSecondary }}>{dialog.id}</td>
                      <td style={{ padding: '10px 12px', fontSize: '12px', fontWeight: 500, color: theme.textSecondary }}>{dialog.user_name || `user_${dialog.user_id}`}</td>
                      <td style={{ padding: '10px 12px', fontSize: '12px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: theme.textSecondary }}>{dialog.user_question?.substring(0, 50)}...</td>
                      <td style={{ padding: '10px 12px' }}>
                        <span style={{ padding: '2px 8px', borderRadius: '12px', fontSize: '10px', fontWeight: 500, background: `${getSourceColor(dialog.source)}20`, color: getSourceColor(dialog.source) }}>
                          {getSourceIcon(dialog.source)} {dialog.source === 'bot_qwen' ? 'бот' : dialog.source === 'expert' ? 'эксперт' : 'ожидает'}
                        </span>
                      </td>
                      <td style={{ padding: '10px 12px', fontSize: '11px', color: theme.textSecondary }}>{new Date(dialog.asked_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Пагинация */}
            <div style={{ padding: '16px', borderTop: `1px solid ${theme.border}`, display: 'flex', justifyContent: 'center', gap: '8px' }}>
              <button onClick={() => setDialogPage(Math.max(1, dialogPage - 1))} disabled={dialogPage === 1} style={{ padding: '6px 12px', background: theme.accent, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: dialogPage === 1 ? 0.5 : 1 }}>← Назад</button>
              <span style={{ padding: '6px 12px', color: theme.text }}>Страница {dialogPage} / {Math.ceil(dialogTotal / 20) || 1}</span>
              <button onClick={() => setDialogPage(dialogPage + 1)} disabled={dialogPage >= Math.ceil(dialogTotal / 20)} style={{ padding: '6px 12px', background: theme.accent, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: dialogPage >= Math.ceil(dialogTotal / 20) ? 0.5 : 1 }}>Вперед →</button>
            </div>
          </div>
        )}
        {activeTab === 'knowledge' && (
          <div className="animate-fade">
            {/* Поиск и кнопка добавления */}
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <input 
                type="text" 
                placeholder="🔍 Поиск по вопросам..." 
                value={knowledgeSearch} 
                onChange={(e) => setKnowledgeSearch(e.target.value)} 
                style={{ padding: '10px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '8px', flex: 1, maxWidth: '300px' }} 
              />
              <button 
                onClick={() => setShowAddForm(true)} 
                style={{ padding: '10px 20px', background: theme.accent, color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
              >
                + Добавить вопрос
              </button>
            </div>

            {/* Форма добавления/редактирования */}
            {(showAddForm || editingItem) && (
              <div className="animate-fade" style={{ background: theme.card, borderRadius: '12px', border: `1px solid ${theme.border}`, padding: '20px', marginBottom: '20px' }}>
                <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>{editingItem ? '✏️ Редактировать' : '➕ Новый вопрос'}</h3>
                <input 
                  type="text" 
                  placeholder="Вопрос" 
                  value={formData.question} 
                  onChange={(e) => setFormData({ ...formData, question: e.target.value })} 
                  style={{ width: '100%', padding: '10px', marginBottom: '12px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px' }} 
                />
                <textarea 
                  placeholder="Ответ" 
                  rows={3} 
                  value={formData.answer} 
                  onChange={(e) => setFormData({ ...formData, answer: e.target.value })} 
                  style={{ width: '100%', padding: '10px', marginBottom: '12px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px' }} 
                />
                <input 
                  type="text" 
                  placeholder="Категория" 
                  value={formData.category} 
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })} 
                  style={{ width: '100%', padding: '10px', marginBottom: '16px', background: theme.bg, color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px' }} 
                />
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button 
                    onClick={editingItem ? handleUpdate : handleCreate} 
                    style={{ padding: '10px 20px', background: theme.accent, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                  >
                    Сохранить
                  </button>
                  <button 
                    onClick={cancelForm} 
                    style={{ padding: '10px 20px', background: 'transparent', color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '6px', cursor: 'pointer' }}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}

                        {/* Таблица базы знаний */}
            <div style={{ background: theme.card, borderRadius: '12px', border: `1px solid ${theme.border}`, overflow: 'hidden' }}>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: darkMode ? '#0d1117' : '#f9fafb' }}>
                      <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>ID</th>
                      <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Вопрос</th>
                      <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Категория</th>
                      <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Статус</th>
                      <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', color: theme.textSecondary }}>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {knowledgeList.map((item) => (
                      <tr key={item.id} style={{ borderTop: `1px solid ${theme.border}` }}>
                        <td style={{ padding: '10px 12px', fontSize: '12px', color: theme.textSecondary }}>{item.id}</td>
                        <td style={{ padding: '10px 12px', fontSize: '12px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: theme.textSecondary }}>
                          {item.question.substring(0, 40)}...
                        </td>
                        <td style={{ padding: '10px 12px', fontSize: '12px', color: theme.textSecondary }}>{item.category || 'general'}</td>
                        <td style={{ padding: '10px 12px' }}>
                          <span style={{ padding: '2px 8px', borderRadius: '12px', fontSize: '10px', fontWeight: 500, background: item.is_active ? `${theme.success}20` : `${theme.danger}20`, color: item.is_active ? theme.success : theme.danger }}>
                            {item.is_active ? 'активен' : 'неактивен'}
                          </span>
                        </td>
                        <td style={{ padding: '10px 12px' }}>
                          <button onClick={() => startEdit(item)} style={{ padding: '4px 10px', marginRight: '6px', background: theme.accent, color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}>✏️</button>
                          <button onClick={() => handleDelete(item.id)} style={{ padding: '4px 10px', background: theme.danger, color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}>🗑️</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Пагинация */}
            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '8px' }}>
              <button 
                onClick={() => setKnowledgePage(Math.max(1, knowledgePage - 1))} 
                disabled={knowledgePage === 1} 
                style={{ padding: '6px 12px', background: theme.accent, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: knowledgePage === 1 ? 0.5 : 1 }}
              >
                ← Назад
              </button>
              <span style={{ padding: '6px 12px', color: theme.text }}>Страница {knowledgePage} / {Math.ceil(knowledgeTotal / 20) || 1}</span>
              <button 
                onClick={() => setKnowledgePage(knowledgePage + 1)} 
                disabled={knowledgePage >= Math.ceil(knowledgeTotal / 20)} 
                style={{ padding: '6px 12px', background: theme.accent, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: knowledgePage >= Math.ceil(knowledgeTotal / 20) ? 0.5 : 1 }}
              >
                Вперёд →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;