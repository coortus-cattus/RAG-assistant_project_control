import streamlit as st
import httpx
import asyncio
import json

# Функция для отправки запроса к ассистенту
async def ask_assistant(query: str, context: str):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  # Увеличиваем таймаут до 120 секунд
            response = await client.post(
                "http://127.0.0.1:8000/assistant/ask",
                json={"query": query, "context": context},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            st.write(f"HTTP-статус: {response.status_code}")
            st.write(f"Содержимое ответа: {response.text}")
            return response
    except httpx.ReadTimeout as e:
        st.error(f"Ошибка таймаута при запросе к ассистенту: {str(e)}")
        raise
    except httpx.HTTPStatusError as e:
        st.error(f"Ошибка HTTP: {str(e)}")
        raise
    except Exception as e:
        st.error(f"Неизвестная ошибка при запросе к ассистенту: {str(e)}")
        raise

# Функция для добавления контекста
async def add_context(text: str):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  # Увеличиваем таймаут
            response = await client.post(
                "http://127.0.0.1:8000/assistant/add_context",
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            st.write(f"HTTP-статус: {response.status_code}")
            st.write(f"Содержимое ответа: {response.text}")
            return response
    except httpx.ReadTimeout as e:
        st.error(f"Ошибка таймаута при добавлении контекста: {str(e)}")
        raise
    except httpx.HTTPStatusError as e:
        st.error(f"Ошибка HTTP при добавлении контекста: {str(e)}")
        raise
    except Exception as e:
        st.error(f"Неизвестная ошибка при добавлении контекста: {str(e)}")
        raise

# Функция для загрузки данных Trello
async def load_trello():
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  # Увеличиваем таймаут
            response = await client.post("http://127.0.0.1:8000/assistant/load_trello")
            response.raise_for_status()
            st.write(f"HTTP-статус: {response.status_code}")
            st.write(f"Содержимое ответа: {response.text}")
            return response
    except httpx.ReadTimeout as e:
        st.error(f"Ошибка таймаута при загрузке Trello: {str(e)}")
        raise
    except httpx.HTTPStatusError as e:
        st.error(f"Ошибка HTTP при загрузке Trello: {str(e)}")
        raise
    except Exception as e:
        st.error(f"Неизвестная ошибка при загрузке Trello: {str(e)}")
        raise

# Интерфейс Streamlit
st.title("Ассистент на базе RAG")

# Поле для ввода запроса
query = st.text_input("Введите ваш запрос:", "")

# Поле для ввода контекста
context = st.text_area("Введите контекст (опционально):", "")

# Кнопка для отправки запроса
if st.button("Отправить запрос"):
    if query:
        try:
            response = asyncio.run(ask_assistant(query, context))
            if response.status_code == 200:
                st.success("Запрос успешно обработан!")
                st.write(response.json().get("answer"))
            else:
                st.error("Ошибка при обработке запроса")
        except Exception as e:
            st.error(f"Ошибка при отправке запроса: {str(e)}")
    else:
        st.warning("Пожалуйста, введите запрос")

# Кнопка для добавления контекста
if st.button("Добавить контекст"):
    if context:
        try:
            response = asyncio.run(add_context(context))
            if response.status_code == 200:
                st.success("Контекст успешно добавлен!")
            else:
                st.error("Ошибка при добавлении контекста")
        except Exception as e:
            st.error(f"Ошибка при добавлении контекста: {str(e)}")
    else:
        st.warning("Пожалуйста, введите контекст")

# Кнопка для загрузки данных Trello
if st.button("Загрузить данные Trello"):
    try:
        response = asyncio.run(load_trello())
        if response.status_code == 200:
            st.success("Данные Trello успешно загружены!")
        else:
            st.error("Ошибка при загрузке Trello")
    except Exception as e:
        st.error(f"Ошибка при загрузке Trello: {str(e)}")