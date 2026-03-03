'use client';

import { useState } from 'react';
import styles from './cards.module.css';

interface CardTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
}

const templateCategories = [
  { id: 'customer_service', name: '客服类' },
  { id: 'business', name: '商务类' },
  { id: 'survey', name: '问卷调查类' },
  { id: 'appointment', name: '预约类' },
  { id: 'order', name: '订单类' },
  { id: 'info', name: '信息收集类' },
];

// 模拟内置模板数据
const mockTemplates: CardTemplate[] = [
  { id: 'cs_welcome', name: '客服欢迎', description: '标准客服欢迎语卡片', category: 'customer_service' },
  { id: 'cs_menu', name: '客服菜单', description: '常见问题菜单', category: 'customer_service' },
  { id: 'biz_contact', name: '商务名片', description: '商务联系卡片', category: 'business' },
  { id: 'biz_meeting', name: '会议邀约', description: '会议邀约卡片', category: 'business' },
  { id: 'survey_satisfaction', name: '满意度调查', description: '标准满意度调查', category: 'survey' },
  { id: 'appointment_general', name: '通用预约', description: '通用预约表单', category: 'appointment' },
  { id: 'order_status', name: '订单状态', description: '订单状态查询卡片', category: 'order' },
  { id: 'order_confirm', name: '订单确认', description: '订单确认卡片', category: 'order' },
  { id: 'info_feedback', name: '意见反馈', description: '意见反馈表单', category: 'info' },
];

export default function CardBuilderPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<CardTemplate | null>(null);
  const [cardJson, setCardJson] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'templates' | 'editor' | 'preview'>('templates');

  // 过滤模板
  const filteredTemplates = selectedCategory === 'all' 
    ? mockTemplates 
    : mockTemplates.filter(t => t.category === selectedCategory);

  // 选择模板
  const handleSelectTemplate = (template: CardTemplate) => {
    setSelectedTemplate(template);
    setActiveTab('preview');
    // 模拟获取模板 JSON
    setCardJson(JSON.stringify({
      header: { title: { content: template.name }, template: 'blue' },
      elements: [
        { tag: 'div', text: { tag: 'lark_md', content: template.description } }
      ]
    }, null, 2));
  };

  // 更新 JSON
  const handleJsonChange = (json: string) => {
    setCardJson(json);
    try {
      JSON.parse(json);
    } catch (e) {
      // JSON 格式错误
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🎴 飞书卡片管理</h1>
        <p>创建和管理飞书交互卡片</p>
      </div>

      <div className={styles.tabs}>
        <button 
          className={`${styles.tab} ${activeTab === 'templates' ? styles.active : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          📋 模板市场
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'editor' ? styles.active : ''}`}
          onClick={() => setActiveTab('editor')}
        >
          ✏️ JSON 编辑器
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'preview' ? styles.active : ''}`}
          onClick={() => setActiveTab('preview')}
        >
          👁️ 预览
        </button>
      </div>

      <div className={styles.content}>
        {activeTab === 'templates' && (
          <div className={styles.templatePanel}>
            <div className={styles.categoryFilter}>
              <select 
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className={styles.select}
              >
                <option value="all">全部分类</option>
                {templateCategories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div className={styles.templateGrid}>
              {filteredTemplates.map(template => (
                <div 
                  key={template.id}
                  className={`${styles.templateCard} ${selectedTemplate?.id === template.id ? styles.selected : ''}`}
                  onClick={() => handleSelectTemplate(template)}
                >
                  <h3>{template.name}</h3>
                  <p>{template.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'editor' && (
          <div className={styles.editorPanel}>
            <textarea
              className={styles.jsonEditor}
              value={cardJson}
              onChange={(e) => handleJsonChange(e.target.value)}
              placeholder='在这里输入卡片 JSON...'
              spellCheck={false}
            />
            <div className={styles.editorActions}>
              <button className={styles.btnPrimary}>💾 保存</button>
              <button className={styles.btnSecondary}>📋 复制</button>
              <button className={styles.btnSecondary}>🗑️ 清空</button>
            </div>
          </div>
        )}

        {activeTab === 'preview' && (
          <div className={styles.previewPanel}>
            <div className={styles.previewHeader}>
              <h3>卡片预览</h3>
              <span className={styles.badge}>JSON</span>
            </div>
            <pre className={styles.previewJson}>
              {cardJson || '请先选择模板或编辑 JSON'}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
