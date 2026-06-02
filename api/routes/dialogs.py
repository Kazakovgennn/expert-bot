from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from api.dependencies import get_current_user
from db.sync_db import get_connection

router = APIRouter()

class DialogResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str]
    user_question: str
    final_answer: Optional[str]
    source: Optional[str]
    confidence: Optional[int]
    asked_at: datetime
    answered_at: Optional[datetime]

@router.get("/")
async def get_dialogs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    source: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Получить список диалогов с пагинацией и фильтрацией"""
    offset = (page - 1) * limit
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Базовый запрос
    query = "SELECT * FROM dialog_logs WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    
    if source:
        query += " AND source = %s"
        params.append(source)
    
    # Считаем общее количество
    count_query = query.replace("*", "COUNT(*)")
    cur.execute(count_query, params)
    total = cur.fetchone()['count']
    
    # Получаем данные с пагинацией
    query += " ORDER BY id DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    dialogs = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        "data": dialogs,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }

@router.get("/{dialog_id}")
async def get_dialog(dialog_id: int, user: dict = Depends(get_current_user)):
    """Получить конкретный диалог"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM dialog_logs WHERE id = %s", (dialog_id,))
    dialog = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not dialog:
        raise HTTPException(status_code=404, detail="Dialog not found")
    
    return dialog

@router.get("/stats/summary")
async def get_stats_summary(user: dict = Depends(get_current_user)):
    """Получить сводную статистику"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN source IN ('bot_qwen', 'bot_rag') THEN 1 ELSE 0 END) as bot_answered,
            SUM(CASE WHEN source = 'expert' THEN 1 ELSE 0 END) as expert_answered,
            SUM(CASE WHEN source = 'pending_expert' THEN 1 ELSE 0 END) as pending
        FROM dialog_logs
    """)
    stats = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return stats
