# Импортируем Pydantic для создания моделей
from pydantic import BaseModel, Field
# Импортируем тип для списка векторов
from typing import List

# Модель для запроса пользователя к ассистенту
class UserQuery(BaseModel):
    # Запрос (вопрос, например, "Какие задачи в процессе?")
    query: str = Field(..., min_length=1, max_length=500)
    # Контекст (например, данные Trello или дополнительная информация)
    context: str | None = None  # Делаем context опциональным

# Модель для добавления текста в ChromaDB
class TextContext(BaseModel):
    # Текст для векторизации и хранения
    text: str = Field(..., min_length=1, max_length=10000)

# Модель для ответа ассистента
class AssistantResponse(BaseModel):
    # Ответ, сгенерированный LLM
    answer: str

# Модель для отладки векторов (необязательная)
class VectorResponse(BaseModel):
    # Список чисел, представляющих эмбеддинг
    vectors: List[float]