from core.rag import KnowledgeBase

kb = KnowledgeBase()

# Добавляем тестовые вопросы-ответы
test_data = [
    (1, "сколько будет 2+2", "2 + 2 = 4"),
    (2, "как тебя зовут", "Меня зовут ЭкспертБот. Я виртуальный помощник."),
    (3, "кто создал этот бот", "Бот разработан командой экспертов для демонстрации возможностей RAG."),
]

for qa_id, question, answer in test_data:
    kb.add_qa(qa_id, question, answer)
    print(f"✅ Добавлен: {question} -> {answer}")

print("\n🎉 База знаний заполнена тестовыми данными!")
