import os
import openai
from token_ai_new import token_ai, tok_for_bot
from aiogram import Bot, Dispatcher, executor, types
from pathlib import Path
from convert_audio import STT



# openai.api_key = os.getenv(token_ai)
openai.api_key = token_ai
stt = STT()
# bot = telebot.TeleBot(tok_for_bot)
bot = Bot(token=tok_for_bot)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def answer(message: types.Message):
    await message.answer('Привет, я твой лучший друг). Ты можешь задать мне абсолютно любой вопрос.')

@dp.message_handler(content_types=[types.ContentType.TEXT])
async def answer(message: types.Message):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=message.text,
      temperature=0.5,
      max_tokens=2000,
      top_p=1.0,
      frequency_penalty=0.5,
      presence_penalty=0.0,
      # stop=["/n"]
    )
    # print(message.from_user.username, message.text)
    await message.answer(response["choices"][0]["text"].strip())

@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
    ]
)
async def voice_message_handler(message: types.Message):
  if message.content_type == types.ContentType.VOICE:
    file_id = message.voice.file_id
  else:
    await message.reply('Не могу распознать формат сообщения, принимаю только текс или аудио.')
    return
  file = await bot.get_file(file_id)
  file_path = file.file_path
  home = Path.home()
  file_on_disk = Path(home, "", f"{file_id}.wav")
  await bot.download_file(file_path, destination=file_on_disk)
  # print(file_on_disk)
  response = openai.Completion.create(
      model="text-davinci-003",
      prompt=stt.audio_to_text(file_on_disk),
      temperature=0.5,
      max_tokens=2000,
      top_p=1.0,
      frequency_penalty=0.5,
      presence_penalty=0.0,
      # stop=["/n"]
  )
  # print(message.from_user.username, message.text)
  os.remove(file_on_disk)
  await message.answer(response["choices"][0]["text"].strip())

  # await message.answer(stt.audio_to_text(file_on_disk))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
