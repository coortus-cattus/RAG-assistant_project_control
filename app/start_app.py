# Импортируем FastAPI для создания приложения
from fastapi import FastAPI
# ORJSONResponse для быстрой сериализации JSON
from fastapi.responses import ORJSONResponse
# Функции для генерации HTML-документации (Swagger UI и ReDoc)
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

# Функция создает и настраивает FastAPI-приложение
# create_custom_static_urls: если True, добавляем кастомные маршруты документации
def start_app(create_custom_static_urls: bool = False) -> FastAPI:
    # Создаем приложение с названием и версией
    # default_response_class=ORJSONResponse ускоряет ответы
    # docs_url и redoc_url отключаем для кастомных маршрутов
    app = FastAPI(
        title="Trello RAG Assistant",
        version="0.1.0",
        default_response_class=ORJSONResponse,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )
    # Если включены кастомные маршруты, регистрируем их
    if create_custom_static_urls:
        register_static_docs_routes(app)
    return app

# Функция добавляет кастомные маршруты для документации
def register_static_docs_routes(app: FastAPI):
    # Маршрут /docs для Swagger UI
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        # Генерируем HTML для Swagger UI
        # openapi_url — путь к OpenAPI-схеме
        # title — заголовок страницы
        # swagger_js_url и swagger_css_url — файлы из папки static
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    # Маршрут для OAuth-редиректа Swagger UI
    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        # Возвращаем HTML для редиректа
        return get_swagger_ui_oauth2_redirect_html()

    # Маршрут /redoc для ReDoc
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        # Генерируем HTML для ReDoc
        # redoc_js_url — файл из папки static
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )