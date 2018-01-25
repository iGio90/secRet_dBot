import asyncio
from threading import Thread

from aiohttp.web import Application, json_response, run_app


class SecRetRest(object):
    def __init__(self, secret_context):
        # secret context
        self.secret_context = secret_context

        # create the event loop
        self.event_loop = asyncio.new_event_loop()

    async def init(self):
        app = Application(loop=self.event_loop)
        app.router.add_get('/', self.status)
        return app

    def start(self):
        rest = Thread(target=self.up_rest)
        rest.start()

    def up_rest(self):
        app = self.event_loop.run_until_complete(self.init())
        run_app(app, loop=self.event_loop, handle_signals=False)

    ##
    # routers
    ##

    async def status(self, request):
        res = self.secret_context.handler_status.get_status()
        return json_response(res)

