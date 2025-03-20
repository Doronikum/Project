import logging
import os
from telebot import TeleBot
from telebot.types import Voice
from gtts import gTTS
import tempfile
import requests
from openai import OpenAI

# Инициализация клиента OpenAI
client = OpenAI(
    api_key="sk-eojihWMYuwlwO4oNjNMX8DbkkkBtLg7I",
    base_url="https://api.proxyapi.ru/openai/v1"
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.environ.get("TOKEN")
bot = TeleBot(TOKEN)

def generate_audio(text):
    """Генерирует аудиофайл из текста."""
    tts = gTTS(text=text, lang='ru')
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        tts.save(tmp.name)
        return tmp.name

def get_openai_response(question):
    """Получает ответ от OpenAI."""
    response = requests.post(
        f"{client.base_url}/completions",
        headers={"Authorization": f"Bearer {client.api_key}"},
        json={
            "model": "text-davinci-003",
            "prompt": question,
            "max_tokens": 2048,
            "temperature": 0.7,
        }
    )
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("text", "")
    else:
        return "Ошибка при получении ответа от OpenAI."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я готов ответить на ваши вопросы.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    question = message.text
    if question.startswith('/'):
        return
    response = get_openai_response(question)
    audio_file = generate_audio(response)
    with open(audio_file, 'rb') as f:
        bot.send_voice(message.chat.id, f, caption=response)
    os.remove(audio_file)

bot.polling()
