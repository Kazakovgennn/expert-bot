import logging
import lancedb
import pyarrow as pa
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
from core.config import settings

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self):
        """Инициализация LanceDB (векторная БД)"""
        self.db = lancedb.connect("./lancedb_data")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.vector_size = 384
        self.cache = {}
        
        # Схема таблицы: id, вопрос, ответ, вектор
        self.schema = pa.schema([
            pa.field("id", pa.int64()),
            pa.field("question", pa.string()),
            pa.field("answer", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), self.vector_size)),
        ])
        
        # Создаём или открываем таблицу
        try:
            self.table = self.db.create_table("knowledge", schema=self.schema, mode="overwrite")
            logger.info("✅ Создана новая таблица в LanceDB")
        except Exception:
            self.table = self.db.open_table("knowledge")
            logger.info("✅ Открыта существующая таблица в LanceDB")
        
        # Синхронизация с PostgreSQL
        self._sync_from_postgres()
    
    def _get_embedding(self, text: str):
        """Получает вектор текста"""
        return self.encoder.encode(text).tolist()
    
    def _sync_from_postgres(self):
        """Синхронизирует LanceDB с PostgreSQL"""
        from db.sync_db import get_connection
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, question, answer FROM knowledge WHERE is_active = true")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            for row in rows:
                qa_id, question, answer = row
                self.add_qa(qa_id, question, answer)
            
            logger.info(f"✅ Синхронизировано {len(rows)} вопросов из PostgreSQL")
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации: {e}")
    
    def add_qa(self, qa_id: int, question: str, answer: str):
        """Добавляет вопрос-ответ в базу знаний"""
        try:
            vector = self._get_embedding(question)
            self.table.add([{
                "id": qa_id,
                "question": question,
                "answer": answer,
                "vector": vector
            }])
            self.cache.clear()
            logger.info(f"✅ Добавлен вопрос #{qa_id} в LanceDB: {question[:50]}")
        except Exception as e:
            logger.error(f"❌ Ошибка добавления в LanceDB: {e}")
    
    def find_similar(self, query: str, threshold: int = None):
        """Ищет похожий вопрос в базе знаний"""
        if threshold is None:
            threshold = settings.RAG_SIMILARITY_THRESHOLD
        
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Получаем вектор запроса
            query_vector = self._get_embedding(query)
            
            # Ищем в LanceDB
            results = self.table.search(query_vector).limit(1).to_list()
            
            if not results:
                return None, 0, None
            
            best = results[0]
            vector_score = best["_distance"]  # LanceDB возвращает расстояние
            
            # Конвертируем расстояние в проценты (чем меньше расстояние, тем выше схожесть)
            # Расстояние 0 = идентично, ~1.5 = непохоже
            similarity = max(0, (1 - vector_score / 2) * 100)
            
            found_question = best["question"]
            
            # Fuzzy-поиск для точных совпадений
            fuzzy_score = fuzz.ratio(query.lower(), found_question.lower())
            final_score = max(similarity, fuzzy_score)
            
            if final_score >= threshold:
                answer = best["answer"]
                qa_id = best["id"]
                result = (answer, int(final_score), qa_id)
                self.cache[cache_key] = result
                logger.info(f"✅ Найдено: '{found_question[:50]}' (уверенность: {int(final_score)}%)")
                return result
            
            return None, int(final_score), None
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска в LanceDB: {e}")
            return None, 0, None
