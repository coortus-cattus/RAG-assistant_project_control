# Импортируем ABC для создания абстрактного класса
from abc import ABC, abstractmethod
# Импортируем тип коллекции ChromaDB
from chromadb import Collection
# Импортируем Agent для работы с LLM (Ollama)
from pydantic_ai import Agent

# Абстрактный интерфейс репозитория
class AbstractRepository(ABC):
    # Метод для добавления документа
    @abstractmethod
    async def add_document(self, document: str, collection: Collection) -> str:
        pass

    # Метод для выполнения запроса
    @abstractmethod
    async def query(self, query: str, collection: Collection) -> str:
        pass

# Реализация репозитория для ChromaDB и LLM
class ChromaRepository(AbstractRepository):
    def __init__(self):
        # Инициализируем Agent без параметров, полагаясь на конфигурацию по умолчанию
        self.agent = Agent()

    async def add_document(self, document: str, collection: Collection) -> str:
        # Очищаем текст от лишних пробелов
        cleaned_text = " ".join(document.strip().split())
        # Добавляем документ в ChromaDB с уникальным ID
        collection.add(documents=[cleaned_text], ids=[f"doc_{hash(cleaned_text)}"])
        # Возвращаем очищенный текст
        return cleaned_text

    async def query(self, query: str, collection: Collection) -> str:
        # Ищем до 3 релевантных документов в ChromaDB
        results = collection.query(query_texts=[query], n_results=3)
        # Собираем найденные документы в контекст
        context = "\n".join(results["documents"][0]) if results["documents"] else ""
        # Формируем промпт для LLM
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        # Запрашиваем ответ у LLM
        response = await self.agent.query(prompt)
        # Возвращаем ответ
        return response