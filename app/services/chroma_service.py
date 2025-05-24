import logging
from chromadb import Collection
from trello import TrelloClient
from db.chroma_repository import AbstractRepository
from langchain_community.llms import Ollama
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo
        self.llm = Ollama(model="llama3.2", base_url="http://localhost:11434")

    async def add_document(self, collection: Collection, document: str) -> str:
        logger.info(f"Adding document to Chroma: {document[:50]}...")
        try:
            result = await self.repo.add_document(document, collection)
            logger.info(f"Successfully added document to Chroma")
            return result
        except Exception as e:
            logger.error(f"Failed to add document to Chroma: {str(e)}")
            raise Exception(f"Failed to add document: {str(e)}")

    async def query(self, query: str, collection: Collection) -> str:
        logger.info(f"Received query: {query}")
        try:
            # Поиск релевантных карточек в Chroma
            results = collection.query(query_texts=[query], n_results=3)
            trello_context = "\n".join(results["documents"][0]) if results["documents"] else "Нет данных Trello"
            logger.info(f"Retrieved Trello context: {trello_context[:100]}...")

            # Формируем промпт с найденными данными
            prompt = (
                "Ты ассистент, который помогает с задачами на Trello-доске. "
                "Вот релевантные данные с Trello-доски:\n\n"
                f"{trello_context}\n\n"
                f"Ответь на вопрос: {query}\n"
                "Форматируй ответ как список задач, указывая название, колонку и дедлайн. "
                "Если данные нерелевантны, напиши: 'Нет подходящих задач'."
            )

            # Отправляем запрос в Ollama
            response = await self.llm.ainvoke(prompt)
            logger.info(f"LLM response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing query with LLM: {str(e)}")
            raise Exception(f"Query failed: {str(e)}")

    async def add_trello_cards(self, collection: Collection, board_id: str, trello_client: TrelloClient) -> int:
        logger.info(f"Attempting to fetch board {board_id}")
        try:
            board = trello_client.get_board(board_id)
            logger.info(f"Successfully fetched board {board_id}")
        except Exception as e:
            logger.error(f"Failed to fetch board {board_id}: {str(e)}")
            raise Exception(f"Failed to fetch board: {str(e)}")

        logger.info("Fetching all cards from board")
        try:
            cards = board.all_cards()
            logger.info(f"Successfully fetched {len(cards)} cards")
        except Exception as e:
            logger.error(f"Failed to fetch cards: {str(e)}")
            raise Exception(f"Failed to fetch cards: {str(e)}")

        count = 0
        documents = []
        ids = []
        with open("trello_cards.txt", "w", encoding="utf-8") as f:
            for card in cards:
                logger.info(f"Processing card: {card.name}")
                try:
                    list_name = card.get_list().name
                except Exception as e:
                    logger.error(f"Failed to fetch list for card {card.name}: {str(e)}")
                    list_name = "Неизвестно"

                try:
                    members = []
                    for member_id in card.member_ids:
                        logger.info(f"Fetching member {member_id}")
                        try:
                            member = trello_client.get_member(member_id)
                            members.append(member.fullName)
                        except Exception as e:
                            logger.error(f"Failed to fetch member {member_id}: {str(e)}")
                            members.append(f"Ошибка: {str(e)}")
                    members_str = ", ".join(members) if members else "Нет"
                except Exception as e:
                    logger.error(f"Failed to process members for card {card.name}: {str(e)}")
                    members_str = "Ошибка при получении участников"

                try:
                    due = card.due_date.strftime("%Y-%m-%d") if card.due_date else "Нет"
                except Exception as e:
                    logger.error(f"Failed to process due date for card {card.name}: {str(e)}")
                    due = "Неизвестно"

                try:
                    comments = "\n".join([c["data"]["text"] for c in card.comments]) if card.comments else "Нет"
                except Exception as e:
                    logger.error(f"Failed to process comments for card {card.name}: {str(e)}")
                    comments = "Неизвестно"

                text = f"Задача: {card.name}\nКолонка: {list_name}\nОтветственный: {members_str}\nДедлайн: {due}\nОписание: {card.description or 'Нет'}\nКомментарии: {comments}\n---\n"
                f.write(text)
                documents.append(text)
                ids.append(f"card_{count}")
                count += 1

        # Добавляем карточки в Chroma
        if documents:
            try:
                collection.add(documents=documents, ids=ids)
                logger.info(f"Added {len(documents)} cards to Chroma collection")
            except Exception as e:
                logger.error(f"Failed to add cards to Chroma: {str(e)}")
                raise Exception(f"Failed to add cards to Chroma: {str(e)}")

        logger.info(f"Logged {count} cards from board {board_id}")
        return count