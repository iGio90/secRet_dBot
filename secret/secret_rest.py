import asyncio
import aiohttp_cors

from aiohttp.web import Application, json_response, run_app
from threading import Thread


class SecRetRest(object):
    def __init__(self, secret_context):
        # secret context
        self.secret_context = secret_context

        # create the event loop
        self.event_loop = asyncio.new_event_loop()

    async def init(self):
        # setup app
        app = Application(loop=self.event_loop)

        # setup cors
        cors = aiohttp_cors.setup(app)

        # setup routers
        resource = cors.add(app.router.add_resource("/"))

        cors.add(
            resource.add_route("GET", str), {
                "http://secret.re": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers=("X-SecretServer-Header",),
                    allow_headers=("X-Requested-With", "Content-Type"),
                    max_age=3600,
                )
            })
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

