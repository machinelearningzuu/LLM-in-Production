from src.chatbot_pipe import *
from flask import Flask, request, jsonify
from flask_cors import CORS

chat_pipe = ChatBotPipeline(llm=llm)
app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    ''' chatbot endpoint '''
    
    data = request.get_json()
    question = data['question']
    userid = int(data['userid'])
    answer = chat_pipe.get_answer(
                                userid,
                                question
                                )
    
    return jsonify({
                    "answer": answer
                    })

if __name__ == '__main__':
    app.run(debug=True)