# Импортируем FastAPI для создания API
from fastapi import FastAPI
# CORS для разрешения запросов с веб-интерфейса
from fastapi.middleware.cors import CORSMiddleware
# Подключение статических файлов для документации
from fastapi.staticfiles import StaticFiles
# Маршруты ассистента
from routes.assistant import router as assistant_router
# Функция создания приложения
from start_app import start_app
# Для возврата HTML-ответа
from fastapi.responses import HTMLResponse

# Создаем приложение с кастомными маршрутами документации
app = start_app(create_custom_static_urls=True)
# Монтируем папку static для файлов Swagger UI и ReDoc
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем CORS для Streamlit (веб-интерфейс на localhost:8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем корневой маршрут
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>Trello RAG Assistant</title></head>
        <body>
            <h1>Trello RAG Assistant</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for Swagger UI or <a href="/redoc">/redoc</a> for ReDoc.</p>
        </body>
    </html>
    """

# Подключаем маршруты ассистента
app.include_router(assistant_router)

# Запускаем сервер только при прямом запуске файла
if __name__ == "__main__":
    # Импортируем uvicorn для запуска
    import uvicorn
    # Запускаем на localhost:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)