# Загружаем переменные окружения из .env
from dotenv import load_dotenv
# Pydantic для типобезопасных настроек
from pydantic_settings import BaseSettings
# ChromaDB для векторного хранилища
import chromadb
from chromadb import Client
# Локальная модель для эмбеддингов
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
# Для доступа к переменным окружения
import os

# Загружаем .env при запуске модуля
load_dotenv()

# Кастомная функция эмбеддингов
class LocalEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def __call__(self, texts):
        return self.model.encode(texts).tolist()

# Класс для API-ключей
class Keys(BaseSettings):
    # Ключ Hugging Face больше не нужен, но оставим для совместимости
    HUGGING_FACE_KEY: str = os.getenv("HUGGING_FACE_KEY", "")
    # Ключ и токен Trello API
    TRELLO_API_KEY: str = os.getenv("TRELLO_API_KEY")
    TRELLO_TOKEN: str = os.getenv("TRELLO_TOKEN")
    
# Класс для настройки ChromaDB
class ChromaDB:
    # Модель эмбеддингов
    vector_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Имя коллекции для данных Trello
    collection_name: str = "trello_assistant"

    def __init__(self, hugging_face_key: str = None):  # hugging_face_key не используется
        # Создаем клиент ChromaDB (локальная база)
        self.client = Client()
        # Настраиваем локальные эмбеддинги
        self.embedding_function = LocalEmbeddingFunction(self.vector_model)
        # Создаем или получаем коллекцию
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
        )

# Главный класс настроек
class Settings(BaseSettings):
    # Объявляем поля с типами, необязательные с None по умолчанию
    keys: Keys | None = None
    chroma_db: ChromaDB | None = None
    trello_board_id: str

    # Настраиваем Pydantic для кастомной инициализации
    class Config:
        arbitrary_types_allowed = True  # Разрешаем кастомные типы (ChromaDB)

    def __init__(self, **data):
        super().__init__(**data)
        # Инициализируем ключи, если не переданы
        self.keys = Keys() if self.keys is None else self.keys
        # Инициализируем ChromaDB, если не передан
        self.chroma_db = ChromaDB() if self.chroma_db is None else self.chroma_db
        # Устанавливаем trello_board_id из .env, если не передан
        self.trello_board_id = data.get("trello_board_id", os.getenv("TRELLO_BOARD_ID"))

# Создаем глобальный объект настроек
settings = Settings()