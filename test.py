# from loader import bot
# import asyncio
#
#
# async def main():
#     print(
#         await bot.get_webhook_info()
#     )
#     await bot.close()
#
#
# def test():
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.close()
#
#
# test()

from instapy import InstaPy


app = InstaPy(
    username='_ya_bodya_ya_',
    password='123riko123'
)
print(
    app
)
