from aiohttp import web

async def health_check_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})
