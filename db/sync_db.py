import psycopg2
import psycopg2.extensions

DB_PASSWORD = "123"

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="expert_bot",
        user="postgres",
        password=DB_PASSWORD
    )
    conn.set_client_encoding('UTF8')
    return conn

def save_dialog(user_id, user_name, user_question, final_answer, source, confidence=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dialog_logs (user_id, user_name, user_question, final_answer, source, confidence, asked_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (user_id, user_name, user_question, final_answer, source, confidence))
        log_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Диалог сохранён: {user_question[:50]} (ID={log_id})")
        return log_id
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return None

def update_dialog_answer(log_id, final_answer, source, confidence):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE dialog_logs 
            SET final_answer = %s, source = %s, confidence = %s, answered_at = NOW()
            WHERE id = %s
        """, (final_answer, source, confidence, log_id))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Диалог #{log_id} обновлён: {final_answer[:50]}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")
        return False

def get_stats(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM dialog_logs WHERE user_id = %s", (user_id,))
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dialog_logs WHERE user_id = %s AND source IN ('bot_qwen', 'bot_rag')", (user_id,))
        bot_answered = cur.fetchone()[0]
        cur.close()
        conn.close()
        return total, bot_answered
    except Exception as e:
        print(f"❌ Ошибка статистики: {e}")
        return 0, 0
    
def get_question_by_id(log_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, user_question FROM dialog_logs WHERE id = %s", (log_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {"user_id": row[0], "user_question": row[1]}
        return None
    except Exception as e:
        print(f"❌ Ошибка получения вопроса: {e}")
        return None
