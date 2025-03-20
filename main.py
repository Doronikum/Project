import telebot
from openai import OpenAI
import gtts
import os

# Укажите ваш API-ключ Telegram
TOKEN = "8130551967:AAFyrQevh1rlF368oXC6Zl9cOTC6oHqbUMk"

# Инициализация клиента OpenAI
client = OpenAI(
    api_key="sk-eojihWMYuwlwO4oNjNMX8DbkkkBtLg7I",
    base_url="https://api.proxyapi.ru/openai/v1"
)

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Привет! Нейросеть для выбора лекарств к Вашим услугам!"
                          "Введите название препарата: ")


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "✉️ Просто напишите ваш вопрос, и я отправлю его в GPT-3.5")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Получаем ответ от OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "user", "content": message.text + 'Ты - врач фармацевт сообщаешь о лекарственных препаратах.'
                                                                 'говори серьёзно и кратко. '
                                                                 'ответ построй по пунктам: действующее вещество препарата, '
                                                                 'назначение при заболеваниях, применение - по какой дозе и сколько раз в день, '
                                                                 'если во время еды - сообщи, побочные действия, противопоказания, совместимость с другими препаратами и алкоголем,'
                                                                 ' влияние на управление транспортом. '
                                                                 'По одному предложению на каждый пункт. Номер пункта не называй'}]
        )
        answer = response.choices[0].message.content

        # Преобразуем текст в речь с мужским голосом
        tts = gtts.gTTS(answer, lang='ru', slow=False)
        tts.save("output.mp3")

        # Отправляем голосовое сообщение
        with open("output.mp3", "rb") as audio:
            bot.send_voice(message.chat.id, audio)

        # Удаляем временный файл
        os.remove("output.mp3")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)