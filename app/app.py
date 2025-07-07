import asyncio

from extensions import bot, dp
from views.add_a_workout import router as add_a_workout_router
from views.main import router as main_router
from views.admin import router as admin_router
from views.training_schedule import router as training_sheduler_router
from views.calendar_training import router as calendar_router
from views.start_training import router as start_training_router
from views.training_info import router as info_training_router
from config import settings


async def on_startup():
    """Запускается при старте бота."""
    print("Бот запущен")


async def main():
    """Главная функция."""
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(settings.command_list)

    settings.start_exercise = True
    settings.exercise_list = []
    settings.hour = 0
    settings.date_trainer = ""
    settings.plus_exercise = False
    settings.new_training = True
    settings.training_count = 0
    settings.exercise_count = 0
    dp.include_router(info_training_router)
    dp.include_router(start_training_router)
    dp.include_router(training_sheduler_router)
    dp.include_router(add_a_workout_router)
    dp.include_router(admin_router)
    dp.include_router(calendar_router)
    dp.include_router(main_router)
    dp.startup.register(on_startup)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
