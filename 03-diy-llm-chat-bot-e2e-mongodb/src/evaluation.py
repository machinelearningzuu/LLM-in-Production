import ragas, os
import pandas as pd
import os, nest_asyncio
from datasets import Dataset
from src.chatbot_pipe import *
nest_asyncio.apply() 

class QAEvalPipeline():
    def __init__(self, llm):
        self.qabot = QABot(llm=llm)

    def make_response(
                    self, 
                    question
                    ):
        response = self.qabot.get_answer(question)
        if response is None:
            return ""
        return response

    def load_eval_data(self):
        df = pd.read_csv(path_config.eval_dataset_path)
        df['response'] = df['question'].apply(self.make_response)

        df = df.rename(columns={
                                'context': 'contexts', 
                                'answer': 'ground_truth',
                                'response': 'answer'
                                })
        df['contexts'] = df['contexts'].apply(lambda x: [x])
        eval_data = Dataset.from_dict(df)
        return eval_data

    def ragas_evaluate(self):
        eval_data = self.load_eval_data()
        result_json = ragas.evaluate(
                                    dataset=eval_data,
                                    metrics=[
                                            ragas.metrics.faithfulness,
                                            ragas.metrics.answer_relevancy,
                                            ragas.metrics.context_precision,
                                            ragas.metrics.context_recall
                                            ]
                                )
        result_df = result_json.to_pandas()
        result_df = result_df.fillna(0)
        return result_df

    def evaluation_pipeline(self):
        result_df = self.ragas_evaluate()
        result_df.to_csv(path_config.eval_results_path, index=False)

    def calculate_avg_metrics(self):
        if not os.path.exists(path_config.eval_results_path):
            self.evaluation_pipeline()

        result_df = pd.read_csv(path_config.eval_results_path)
        result_df = result_df[[
                            'faithfulness',
                            'answer_relevancy',
                            'context_precision',
                            'context_recall'
                            ]]
        avg_metrics = result_df.mean()
        return avg_metrics