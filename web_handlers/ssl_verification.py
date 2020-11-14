from aiohttp import web
from aiohttp.web_response import Response


ssl_verification_app = web.Application()


async def ssl_verification(request: web.Request) -> Response:
    return Response(headers={'X-Accel-Redirect': '/.well-known/pki-validation/D9C0B7BE255AC9C5319EE0E989C40809.txt'})


ssl_verification_app.add_routes(
    [web.get('/D9C0B7BE255AC9C5319EE0E989C40809.txt', ssl_verification)]
)
