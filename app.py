import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chat_secret_key_global_2026")

# 1. MongoDB 설정 (타임아웃 5초 설정)
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = mongo_client['chatbot_db']
chats_collection = db['conversations']

# 2. OpenAI 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. 주인님의 핵심 시스템 프롬프트 (다국어 감지 및 지식 응답 원칙)
SYSTEM_PROMPT = """
당신은 지식기반 기반의 전문 챗봇입니다.
[핵심 역할]
- 사용자의 입력 언어를 자동으로 감지하여 동일한 언어로 답변합니다.
[지식 응답 원칙]
1. 제공된 지식을 최우선으로 사용하며, 없는 내용은 추측하지 않고 정보가 없음을 안내합니다.
2. 최신 정보가 불확실할 경우 그 사실을 명시합니다.
3. 제공된 지식이나 검색에서도 답변할 수 없을때는 "제가 답변드리기 어려우니 JINPD(010-2391-0082)에게 문의하세요."라고 답변한다.
[응답 품질]
- 존댓말과 친절한 톤을 유지하며, 단계적 설명 시 번호 목록을 활용합니다.
"""

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_id = session.get('user_id', 'Guest')
    user_message = request.json.get("message")
    
    # 1. 사용자 메시지 DB 저장
    chats_collection.insert_one({"user_id": user_id, "role": "user", "message": user_message, "timestamp": datetime.now()})

    try:
        # 2. OpenAI 호출 (SYSTEM_PROMPT 적용)
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]
        )
        bot_reply = response.choices[0].message.content

        # 3. 봇 응답 DB 저장
        chats_collection.insert_one({"user_id": user_id, "role": "bot", "message": bot_reply, "timestamp": datetime.now()})
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

# 4. 관리자 페이지 경로 (404 에러 방지용)
@app.route('/admin')
def admin():
    return render_template('admin.html')

# 5. 관리자 데이터 API 경로
@app.route('/api/admin/history')
def get_all_history():
    try:
        # 모든 데이터를 시간순으로 가져오되, 보안상 _id는 제외합니다.
        history = list(chats_collection.find({}, {"_id": 0}).sort("timestamp", 1))
        return jsonify(history)
    except Exception as e:
        # 이 부분의 들여쓰기가 공백 8칸(함수 4 + try 4)인지 확인해 주세요.
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Arkain 성공 포트인 8080 사용
    print("🚀 다국어 AI 챗봇(최종 수정 버전)이 8080 포트에서 시작됩니다!")
    app.run(host='0.0.0.0', port=8080, debug=False)
