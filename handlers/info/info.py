from _io import BufferedReader

from aiogram import types

from keyboards.inline.info import get_info_inline_keyboard

from utils.db_api.user.language import get_language
from utils.db_api.info.video import get_videos, save_video_id

from data import config


# Информация
async def info(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    articles_inline_keyboard = await get_info_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu']['info']

    await call_data.message.answer(text_answer, reply_markup=articles_inline_keyboard)


# Отправка видео
async def send_video(call_data: types.CallbackQuery) -> None:
    video_language = call_data.data.replace('get_video ', '')  # example: get_video ru
    videos = await get_videos(video_language)

    text_answer = config.messages[video_language]['info']['video_title']
    await call_data.message.answer(text_answer)

    for video_data in videos:
        for video_model_id, video in video_data:
            if type(video) is BufferedReader:  # если файл был open()
                message = await call_data.message.answer_video(video, width=1080, height=1920)
                video.close()
                await save_video_id(video_model_id, message.video.file_id)
            else:  # по id
                await call_data.message.answer_video(video, width=1080, height=1920)
    await info(call_data)
