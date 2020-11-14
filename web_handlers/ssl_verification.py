import os

from typing import Union

from aiohttp import web
from aiohttp.multipart import CIMultiDict

ssl_verification_app = web.Application()


async def ssl_verification(request: web.Request) -> Union[web.FileResponse, web.Response]:
    file = request.match_info.get("file", None)
    if not file:
        return web.Response(status=404)
    return web.FileResponse(os.path.join("data", file), headers=CIMultiDict({'CONTENT-DISPOSITION': file}))


ssl_verification_app.add_routes(
    [web.get('/{file}', ssl_verification)]
)
