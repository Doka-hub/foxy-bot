from aiogram.dispatcher.filters.state import State, StatesGroup


class PostState(StatesGroup):
    channel_id = State()

    image_id = State()
    title = State()
    text = State()
    button = State()

    date = State()
    time = State()

    edit = State()
    post_id = State()
