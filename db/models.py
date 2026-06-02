from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Knowledge(Base):
    """Таблица базы знаний: вопросы и ответы"""
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False, unique=True, index=True)
    answer = Column(Text, nullable=False)
    
    # Метаданные
    category = Column(String(100), default="general")
    confidence_threshold = Column(Integer, default=85)
    is_active = Column(Boolean, default=True, index=True)
    is_auto_learned = Column(Boolean, default=False)
    
    # Статистика
    times_used = Column(Integer, default=0)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50), default="system")
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'is_active': self.is_active,
            'times_used': self.times_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DialogLog(Base):
    """Логи всех диалогов"""
    __tablename__ = "dialog_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(255))
    user_question = Column(Text, nullable=False)
    
    # Ответы
    bot_answer = Column(Text, nullable=True)
    expert_answer = Column(Text, nullable=True)
    final_answer = Column(Text)
    
    # Метаданные
    confidence = Column(Integer)
    source = Column(String(50))  # 'bot_rag', 'bot_llm', 'expert', 'pending_expert'
    
    # Связи
    knowledge_id = Column(Integer, ForeignKey('knowledge.id'), nullable=True)
    expert_telegram_message_id = Column(Integer)
    
    # Временные метки
    asked_at = Column(DateTime, default=datetime.utcnow, index=True)
    answered_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question': self.user_question,
            'answer': self.final_answer,
            'source': self.source,
            'confidence': self.confidence,
            'asked_at': self.asked_at.isoformat()
        }


class PendingKnowledge(Base):
    """Вопросы, которые ждут подтверждения от эксперта"""
    __tablename__ = "pending_knowledge"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    suggested_answer = Column(Text, nullable=False)
    
    user_id = Column(Integer)
    confidence = Column(Integer)
    status = Column(String(20), default='pending', index=True)  # pending, approved, rejected, edited
    
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(50), nullable=True)


# Индексы для быстрых запросов
Index('idx_dialog_user_date', DialogLog.user_id, DialogLog.asked_at)
Index('idx_knowledge_active', Knowledge.is_active, Knowledge.confidence_threshold)
