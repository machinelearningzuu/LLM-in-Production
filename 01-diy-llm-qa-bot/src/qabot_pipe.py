import pandas as pd
import re, os, time, openai
from src.build_index import *

class QABot():
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
                            "no information", "no context", "don't know", "no clear answer", "sorry", 
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

    def get_answer(self, question):
        ''' get answer to provided question '''

        answer = self._get_answer(question)
        if self._is_good_answer(answer):
            return str(answer)
        else:
            return None