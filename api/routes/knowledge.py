from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from api.dependencies import get_current_user
from db.sync_db import get_connection

router = APIRouter()

class KnowledgeCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = "general"
    confidence_threshold: Optional[int] = 85

class KnowledgeUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    confidence_threshold: Optional[int] = None

@router.get("/")
async def get_knowledge(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    user: dict = Depends(get_current_user)
):
    """Получить список вопросов-ответов с пагинацией и поиском"""
    offset = (page - 1) * limit
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = "SELECT * FROM knowledge WHERE 1=1"
    params = []
    
    if search:
        query += " AND (question ILIKE %s OR answer ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    if is_active is not None:
        query += " AND is_active = %s"
        params.append(is_active)
    
    count_query = query.replace("*", "COUNT(*)")
    cur.execute(count_query, params)
    total = cur.fetchone()['count']
    
    query += " ORDER BY id DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    items = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        "data": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }

@router.get("/{knowledge_id}")
async def get_knowledge_item(knowledge_id: int, user: dict = Depends(get_current_user)):
    """Получить конкретный вопрос-ответ"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM knowledge WHERE id = %s", (knowledge_id,))
    item = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    return item

@router.post("/")
async def create_knowledge(item: KnowledgeCreate, user: dict = Depends(get_current_user)):
    """Создать новый вопрос-ответ"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        INSERT INTO knowledge (question, answer, category, confidence_threshold, created_at, updated_at, created_by)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), %s)
        RETURNING *
    """, (item.question, item.answer, item.category, item.confidence_threshold, user.get('username', 'admin')))
    
    new_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    return new_item

@router.put("/{knowledge_id}")
async def update_knowledge(knowledge_id: int, item: KnowledgeUpdate, user: dict = Depends(get_current_user)):
    """Обновить вопрос-ответ"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Проверяем существование
    cur.execute("SELECT * FROM knowledge WHERE id = %s", (knowledge_id,))
    existing = cur.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    # Строим динамический UPDATE
    updates = []
    params = []
    
    if item.question is not None:
        updates.append("question = %s")
        params.append(item.question)
    
    if item.answer is not None:
        updates.append("answer = %s")
        params.append(item.answer)
    
    if item.category is not None:
        updates.append("category = %s")
        params.append(item.category)
    
    if item.is_active is not None:
        updates.append("is_active = %s")
        params.append(item.is_active)
    
    if item.confidence_threshold is not None:
        updates.append("confidence_threshold = %s")
        params.append(item.confidence_threshold)
    
    if not updates:
        return existing
    
    updates.append("updated_at = NOW()")
    params.append(knowledge_id)
    
    query = f"UPDATE knowledge SET {', '.join(updates)} WHERE id = %s RETURNING *"
    cur.execute(query, params)
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    return updated

@router.delete("/{knowledge_id}")
async def delete_knowledge(knowledge_id: int, user: dict = Depends(get_current_user)):
    """Удалить вопрос-ответ (мягкое удаление — деактивация)"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE knowledge SET is_active = FALSE WHERE id = %s", (knowledge_id,))
    conn.commit()
    rows_affected = cur.rowcount
    cur.close()
    conn.close()
    
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    return {"message": "Knowledge item deactivated"}

@router.get("/categories/list")
async def get_categories(user: dict = Depends(get_current_user)):
    """Получить список всех категорий"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT category FROM knowledge ORDER BY category")
    categories = [row[0] for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {"categories": categories}
