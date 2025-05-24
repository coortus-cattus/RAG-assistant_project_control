# Импортируем настройки из config.py
from config import settings
# Импортируем сервис и репозиторий
from services.chroma_service import ChromaService
from db.chroma_repository import ChromaRepository
# Тип коллекции ChromaDB
from chromadb import Collection

# Функция возвращает коллекцию ChromaDB
def get_collection() -> Collection:
    # Проверяем, что коллекция инициализирована
    if not settings.chroma_db.collection:
        raise RuntimeError("ChromaDB collection not initialized")
    # Возвращаем коллекцию из настроек
    return settings.chroma_db.collection

# Функция возвращает сервис для работы с ChromaDB и Trello
def get_service() -> ChromaService:
    # Создаем сервис с репозиторием
    return ChromaService(ChromaRepository())