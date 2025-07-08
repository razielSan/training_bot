from aiogram.filters import Filter

from aiogram import Bot, types


class IsAdmin(Filter):
    """Фильтр для проверки на администратора."""
    def __init__(self):
        """Инициализация."""
        pass

    async def __call__(self, message: types.Message, bot: Bot):
        """Проверка на администратора."""
        print(message.from_user.id)
        print(bot.my_admins_list)
        print(message.from_user.id in bot.my_admins_list)
        return message.from_user.id in bot.my_admins_list
