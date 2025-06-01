# ✅ MIKA VOICE – מערכת מלאה לשיחה חיה בטלפון עם קול אנושי בעברית
@app.route("/", methods=["GET"])
def index():
    return "🔊 מיקה מוכנה לדבר! השרת פועל בהצלחה."

from flask import Flask, request, Response, send_file
from twilio.twiml.voice_response import VoiceResponse
import openai
import asyncio
import edge_tts
import uuid
import os

# 🔑 OpenAI API שלך
openai.api_key = "sk-ANNUSK9K27RJE7EFSBUZ4929"

app = Flask(__name__)

# 📞 Twilio יקרא לנתיב זה בשיחה נכנסת
@app.route("/voice", methods=["POST"])
def voice():
    vr = VoiceResponse()
    vr.say("שלום, כאן מיקה. איך אני יכולה לעזור?", voice="Polly.Carmit", language="he-IL")
    vr.record(
        timeout=2,
        maxLength=7,
        transcribe=True,
        transcribeCallback="/transcribe",
        playBeep=False
    )
    return Response(str(vr), mimetype='text/xml')

# 🎙️ אחרי שהלקוח מדבר – נשלח לכאן טקסט
@app.route("/transcribe", methods=["POST"])
def transcribe():
    text = request.form.get("TranscriptionText", "")
    print("👂 הלקוח אמר:", text)

    reply = get_reply(text)
    print("🧠 מיקה עונה:", reply)

    filename = f"mika_{uuid.uuid4().hex}.mp3"
    asyncio.run(generate_speech(reply, filename))

    vr = VoiceResponse()
    vr.play(f"https://mika-voice.onrender.com/{filename}")
    vr.redirect("/voice")  # חוזר להתחלה – דו־שיח מלא
    return Response(str(vr), mimetype="text/xml")

# 🧠 מיקה משיבה עם GPT
def get_reply(user_input):
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "את מיקה, מזכירה וירטואלית בישראל. את עונה בטון חברותי, אנושי, חכם."},
            {"role": "user", "content": user_input}
        ]
    )
    return res.choices[0].message.content.strip()

# 🔊 המרת תשובה לקול אנושי בעברית
async def generate_speech(text, filename):
    tts = edge_tts.Communicate(text, voice="he-IL-HilaNeural")
    await tts.save(filename)

# 🎧 שליחה של הקובץ לקו הטלפון
@app.route("/<filename>", methods=["GET"])
def serve_file(filename):
    return send_file(filename, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
