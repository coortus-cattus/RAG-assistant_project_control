# Импортируем FastAPI роутер
from fastapi import APIRouter, Depends, HTTPException
# Импортируем модели
from schemas import UserQuery, AssistantResponse, TextContext
# Импортируем зависимости
from dependencies import get_collection, get_service
from services.chroma_service import ChromaService
# Импортируем Trello клиент
from trello import TrelloClient
# Импортируем исключения Trello
from trello.exceptions import ResourceUnavailable
# Импортируем типы
from chromadb import Collection
from typing import Annotated
# Импортируем настройки
from config import settings

# Создаем роутер с префиксом и тегом
router = APIRouter(prefix="/assistant", tags=["assistant"])

# Зависимость для создания Trello клиента
def get_trello_client() -> TrelloClient:
    return TrelloClient(
        api_key=settings.keys.TRELLO_API_KEY,
        token=settings.keys.TRELLO_TOKEN
    )

# Эндпоинт для добавления текста в ChromaDB
@router.post("/add_context", response_model=AssistantResponse)
async def add_context(
    context: TextContext,
    service: Annotated[ChromaService, Depends(get_service)],
    collection: Annotated[Collection, Depends(get_collection)]
):
    # Добавляем текст в ChromaDB через сервис
    text = await service.add_document(collection, context.text)
    return AssistantResponse(answer=f"Добавлен текст: {text}")

# Эндпоинт для запроса к ассистенту
@router.post("/ask", response_model=AssistantResponse)
async def ask_assistant(
    user_query: UserQuery,
    service: Annotated[ChromaService, Depends(get_service)],
    collection: Annotated[Collection, Depends(get_collection)]
):
    # Добавляем контекст в ChromaDB, только если он предоставлен
    if user_query.context is not None:
        await service.add_document(collection, user_query.context)
    # Выполняем запрос (поиск + LLM)
    answer = await service.query(user_query.query, collection)
    return AssistantResponse(answer=answer)

# Эндпоинт для загрузки данных из Trello
@router.post("/load_trello", response_model=AssistantResponse)
async def load_trello(
    service: Annotated[ChromaService, Depends(get_service)],
    collection: Annotated[Collection, Depends(get_collection)],
    trello_client: Annotated[TrelloClient, Depends(get_trello_client)]
):
    try:
        # Загружаем карточки Trello в ChromaDB
        count = await service.add_trello_cards(collection, settings.trello_board_id, trello_client)
        return AssistantResponse(answer=f"Загружено {count} карточек из Trello")
    except ResourceUnavailable as e:
        # Обрабатываем ошибки Trello API
        raise HTTPException(status_code=400, detail=f"Trello API error: {str(e)}")
    except Exception as e:
        # Обрабатываем остальные ошибки
        raise HTTPException(status_code=500, detail=f"Failed to load Trello data: {str(e)}")