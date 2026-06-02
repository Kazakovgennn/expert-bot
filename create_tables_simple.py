import psycopg2

# ЗАМЕНИ пароль на свой из .env
PASSWORD = "123"

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="expert_bot",
    user="postgres",
    password=PASSWORD
)
cursor = conn.cursor()

# Создаём таблицы
cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id SERIAL PRIMARY KEY,
        question TEXT NOT NULL UNIQUE,
        answer TEXT NOT NULL,
        category VARCHAR(100) DEFAULT 'general',
        confidence_threshold INTEGER DEFAULT 85,
        is_active BOOLEAN DEFAULT TRUE,
        is_auto_learned BOOLEAN DEFAULT FALSE,
        times_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        created_by VARCHAR(50) DEFAULT 'system'
    );
    
    CREATE TABLE IF NOT EXISTS dialog_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        user_name VARCHAR(255),
        user_question TEXT NOT NULL,
        bot_answer TEXT,
        expert_answer TEXT,
        final_answer TEXT,
        confidence INTEGER,
        source VARCHAR(50),
        knowledge_id INTEGER REFERENCES knowledge(id),
        expert_telegram_message_id INTEGER,
        asked_at TIMESTAMP DEFAULT NOW(),
        answered_at TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS pending_knowledge (
        id SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        suggested_answer TEXT NOT NULL,
        user_id INTEGER,
        confidence INTEGER,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW(),
        reviewed_at TIMESTAMP,
        reviewed_by VARCHAR(50)
    );
    
    CREATE INDEX IF NOT EXISTS idx_dialog_user_date ON dialog_logs(user_id, asked_at);
    CREATE INDEX IF NOT EXISTS idx_knowledge_active ON knowledge(is_active, confidence_threshold);
""")

conn.commit()
cursor.close()
conn.close()

print("✅ Таблицы успешно созданы!")
