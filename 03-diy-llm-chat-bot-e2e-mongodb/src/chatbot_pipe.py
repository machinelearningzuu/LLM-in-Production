import pandas as pd
import re, os, time, openai
from src.build_index import *

class ChatBotPipeline():
    def __init__(
                self, 
                llm
                ):
        self.llm = llm
        self.query_engine = index_pipeline()

    def _is_good_answer(
                        self, 
                        answer
                        ):
        ''' check if answer is a valid '''

        result = True
        badanswer_phrases = [
                            "no information", "no context", "don't know", "no clear answer", "sorry", "empty response",
                            "no answer", "no mention", "reminder", "context does not provide", "no helpful answer", 
                            "given context", "no helpful", "no relevant", "no question", "not clear",
                            "don't have enough information", " does not have the relevant information", "does not seem to be directly related"
                            ]
        
        if answer is None:
            result = False
        else:
            for phrase in badanswer_phrases:
                if phrase in str(answer).lower():
                    result = False
                    break
        
        return result
    
    def _get_answer(
                    self,
                    question, 
                    timeout_sec=60
                    ):
        
        '''' get answer from llm with timeout handling '''

        result = None
        end_time = time.time() + timeout_sec

        while time.time() < end_time:
            try: 
                result =  self.query_engine.query(question)
                break

            except openai.error.RateLimitError as rate_limit_error:
                if time.time() < end_time: # if time permits, sleep
                    time.sleep(2)
                    continue

                else:
                    raise rate_limit_error

            except Exception as e:
                print(f'LLM Query Engine encountered unexpected error: {e}')
                raise e

        return result

    def _get_history(
                    self,
                    user_id,
                    question
                    ):
        ''' get chat history for user '''
        user_data = db[db_config.user_collection]
        chat_data = db[db_config.chat_collection]

        user = user_data.find_one({"user_id": user_id})
        if user is None:
            AssertionError(f"User : {user_id} not found in database ...")

        chat_history = chat_data.find_one({"user_id": user_id})
        if chat_history is None:
            chat_history = {
                            "user_id": user_id,
                            "chat_history": []
                            }
            chat_data.insert_one(chat_history)
            history_str = f"USER : {question}"
        else:
            history_str = ""
            for chat in chat_history["chat_history"]:
                history_str += f"USER : {chat['user']}\nBOT : {chat['bot']}\n\n"
            history_str += f"USER : {question}"

        return history_str, chat_data
        
    def get_answer(
                self,
                user_id,
                question
                ):
        ''' get answer to provided question '''

        question_with_history, chat_data = self._get_history(user_id, question)
        answer = self._get_answer(question_with_history)
        answer = str(answer)

        if self._is_good_answer(answer):
            print("RETRIEVING ...")

        else:
            print("NO CONTEXT MATCHED, RE-ASKING LLM ...")
            answer = llm.complete(
                                prompt=llm_config.human_message_template.format(
                                                                            context='',
                                                                            question=question_with_history
                                                                            ),
                                max_tokens=100,
                                temperature=llm_config.temperature
                                )
            answer = str(answer)

        new_chat = {
                    "user": question,
                    "bot": answer
                    }
        chat_data.update_one(
                            {"user_id": user_id},
                            {"$push": {"chat_history": new_chat}}
                            )
        return answer