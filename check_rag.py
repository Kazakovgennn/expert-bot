from core.rag import KnowledgeBase

kb = KnowledgeBase()

# Проверяем поиск
test_queries = [
    "сколько будет 2+2",
    "как тебя зовут",
    "кто создал бота"
]

for query in test_queries:
    answer, confidence, qa_id = kb.find_similar(query)
    if answer:
        print(f"🔍 Вопрос: {query}")
        print(f"✅ Найдено: {answer} (уверенность: {confidence}%)\n")
    else:
        print(f"❌ Вопрос: {query} - ничего не найдено\n")
