from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from typing import Tuple, Any

from utils.db_api.language import get_language

from data.config import I18N_DOMAIN, LOCALES_DIR


class LanguageMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        return await get_language(user_id=user.id) or user.locale


i18n = LanguageMiddleware(I18N_DOMAIN, LOCALES_DIR)
