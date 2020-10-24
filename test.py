from loader import bot
import asyncio


async def main():
    print(
        await bot.get_webhook_info()
    )
    await bot.close()


def test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


test()
