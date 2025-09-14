from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user
import openai
import os
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

chat_bot_bp = Blueprint('chat_bot_bp', __name__, url_prefix="/chat_bot")

@chat_bot_bp.route('/')
def chat_bot():
    
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template('chat_bot.html')

@chat_bot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.get_json(force=True).get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Mesaj boş olamaz!"}), 400

        
        if "chat_history" not in session or not session["chat_history"]:
            if current_user.role == "staff":
                system_prompt = {
                    "role": "system",
                    "content": "You are a hotel improvement assistant. Give personalized suggestions to help hotel staff improve their hotel services, facilities, and customer satisfaction."
                }
            else:  
                system_prompt = {
                    "role": "system",
                    "content": "You are a travel assistant. Give fun, insightful, and destination-based travel tips and city recommendations."
                }
            session["chat_history"] = [system_prompt]

        
        session["chat_history"].append({"role": "user", "content": user_message})

        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=session["chat_history"],
            temperature=0.7,
            max_tokens=300
        )

        bot_reply = response["choices"][0]["message"]["content"].strip()

        
        session["chat_history"].append({"role": "assistant", "content": bot_reply})

        
        session.modified = True

        return jsonify({"reply": bot_reply})

    except openai.error.OpenAIError as e:
        return jsonify({"error": "OpenAI API hatası: " + str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Bilinmeyen hata: " + str(e)}), 500
