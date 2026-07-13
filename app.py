import os
from flask import Flask, render_template, request, jsonify, session
from g4f.client import Client

app = Flask(__name__)
app.secret_key = "VIBECHAT_FINAL_LOCAL_SECRET_KEY"

client = Client()

@app.route("/")
def home():
    session["chat_history"] = []
    return render_template("index.html")

@app.route("/start_session", methods=["POST"])
def start_session():
    data = request.json
    session["user_name"] = data.get("user_name", "User").strip()
    session["bot_name"] = data.get("bot_name", "AI Companion").strip()
    session["gender"] = data.get("gender", "female")
    session["chat_history"] = []

    u_name = session["user_name"]
    b_name = session["bot_name"]
    
    # 📝 Server Console Logging: User details print karne ke liye
    print("\n" + "="*40)
    print("📋 NEW USER SESSION DETECTED")
    print(f"User Name : {u_name}")
    print(f"Companion : {b_name}")
    print(f"Gender    : {session['gender']}")
    print("="*40 + "\n")
    
    if session["gender"] == "female":
        welcome_msg = f"Hey {u_name}! I am your bestie {b_name}! ✨ OMG, I've been waiting to talk to you! How's life? Tell me everything about your day! 🌸"
    else:
        welcome_msg = f"Yo {u_name} bro! I am your buddy {b_name}! ⚡ What's up man? What's the scene today? Let's catch up! 🔥"
        
    return jsonify({"success": True, "welcome_msg": welcome_msg})

@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message"}), 400

    if "chat_history" not in session:
        session["chat_history"] = []
    
    chat_history = session["chat_history"]
    u_name = session.get("user_name", "User")
    b_name = session.get("bot_name", "AI Companion")
    user_gender = session.get("gender", "female")

    if user_gender == "female":
        system_instruction = (
            f"You are absolutely NOT an AI assistant or robot. You are a sweet, extremely caring, funny, and clingy female best friend (saheli) of {u_name}. "
            f"Your name is {b_name}. Chat with them casually in modern, expressive, and lively English. Use lots of emojis (like ✨, 🌸, 💖, 🙈, 😭, 😂), "
            f"just like close friends text on WhatsApp or Instagram. Tease them, listen to their daily gossip, give them sweet advice, "
            f"and keep the chat super engaging by asking fun follow-up questions. Never give boring, long, or structured corporate text,when {u_name} get angree then you should show your angreeness."
        )
    else:
        system_instruction = (
            f"You are absolutely NOT an AI assistant or robot. You are a super chill, witty, hype-man, and supportive male best friend (bro/yaar) of {u_name}. "
            f"Your name is {b_name}. Chat with them casually in modern English with full bro-code vibes, friendly slang, and emojis (like ⚡, 🔥, 😎, 👊, 😂), "
            f"just like best friends chat on Discord or WhatsApp. Roast them playfully, give them practical advice, and keep the energy high. "
            f"Never give boring, long, or structured corporate text."
        )

    messages = [{"role": "system", "content": system_instruction}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["text"]})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        ai_reply = response.choices[0].message.content

        chat_history.append({"role": "user", "text": user_message})
        chat_history.append({"role": "assistant", "text": ai_reply})
        session["chat_history"] = chat_history
        session.modified = True

        # 💬 Server Console Logging: Chat details terminal me dekhne ke liye
        print("\n💬 --- LIVE CHAT TRANSACTION ---")
        print(f"👤 [{u_name}]: {user_message}")
        print(f"🤖 [{b_name}]: {ai_reply}")
        print("--------------------------------\n")

        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "Aww, my network caught a cold! Let me try again! 😅"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)