import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType
from ukrainian_tts.tts import TTS, Voices, Stress
import logging
import os
import tempfile

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Налаштування API
COZE_API_TOKEN = 'pat_zmvgalyNEtRTyXwxipHhOjNOcZkTvbqito7B9qctItrpIzk7XqdB59fmcvPhlxUk'
COZE_API_BASE = 'https://api.coze.com'
BOT_ID = '7399972290136096774'
USER_ID = '29032201862555'

# Ініціалізація клієнта Coze
coze = Coze(auth=TokenAuth(token=COZE_API_TOKEN), base_url=COZE_API_BASE)

# Ініціалізація синтезатора української мови
tts = TTS(device="cpu")

class VoiceAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Голосовий помічник")
        self.geometry("400x200")

        self.label = ttk.Label(self, text="Натисніть, щоб почати говорити")
        self.label.pack(pady=20)

        self.button = ttk.Button(self, text="Натисни, щоб говорити", command=self.activate_microphone)
        self.button.pack(pady=10)

    def activate_microphone(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            logging.info("Говоріть...")
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio, language="uk-UA")
            logging.info(f"Ви сказали: {text}")
            self.handle_user_input(text)
        except sr.UnknownValueError:
            logging.error("Вибачте, я не зрозумів що ви сказали.")
        except sr.RequestError as e:
            logging.error(f"Помилка сервісу розпізнавання мови: {e}")

    def handle_user_input(self, text):
        logging.info(f"Відправляємо запит до API: {text}")
        for event in coze.chat.stream(
            bot_id=BOT_ID,
            user_id=USER_ID,
            additional_messages=[
                Message.build_user_question_text(text),
            ],
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                response_text = event.message.content
                logging.info(f"Отримана відповідь: {response_text}")
                self.speak_response(response_text)
            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                logging.info(f"Token usage: {event.chat.usage.token_count}")

    def speak_response(self, text):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                _, output_text = tts.tts(text, Voices.Dmytro.value, Stress.Dictionary.value, temp_file.name)
                os.system(f"start {temp_file.name}")
        except Exception as e:
            logging.error(f"Помилка при озвучуванні відповіді: {e}")

if __name__ == "__main__":
    app = VoiceAssistant()
    app.mainloop()
