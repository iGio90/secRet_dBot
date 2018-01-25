# Documentation

### Something running that you can access for code your stuffs:
* discord (http://discordpy.readthedocs.io/en/latest/api.html)
* github (http://pygithub.readthedocs.io/en/latest/github.html)
* mongo db (http://docs.mongoengine.org/apireference.html)
* http server and rest api (WIP)

A lot of things are just not exposed by design (I.E wikipedia api, weather).
This mean, that we have them inside but not exposed. References could be created as needed!


---

### Add commands and features
1) add your command to the commands map ``commands/map/user_commands.json``
2) eventually, add a shortcut for it ``commands/map/shortcuts.json``
3) code the root handler in ``message_handler.py``

```python
async def roll(self, message):
    """
    simple roll accepting max as first arg
    """
    parts = message.content.split(" ")
    max = 100
    if len(parts) > 1:
        try:
            max = int(parts[1])
        except Exception as e:
            pass

    embed = utils.simple_embed('roll', '**' + str(random.randint(0, max)) + '**', utils.random_color())
    await self.discord_client.send_message(message.channel, embed=embed)
```

A simple function like that could be coded straight inside the message_handler.

**Things to follow:**
1) function must be preceded by ``async`` to use asyncio
2) the api to send a message through discord must be sent using asyncio as well: ``await self.discord_client.send_message``
3) function list is alphabetically ordered for a better read. keep this.
4) object ``message`` is **mandatory argument** to any function in the map and provide discord api (server, channel, members etc.)

If you like to code advanced and more complex stuffs, you can add your classes to ``commands/`` package.
A little example from ``message_handler.py``:

```python
async def wikipedia(self, message):
    await wikipedia.on_message(message, self.discord_client, self.bus)
```

---

### Give your classes something to use from the message handler

I think there is no need of so much description if you are arrived here.

```python
# hold the last command used
self.last_command = {}
# ctor time
self.start_time = datetime.now().timestamp()
# event bus.
# we have some handlers all around.
# feel free to register and use it to spread stuffs from different threads
self.bus = bus
# the discord client providing api with our discord server
self.discord_client = discord_client
# a mongo db.
# checkout mongo_models for some example of usage case
self.mongo_db = mongo_db
# hold a reference of both channel and server.
# sometime we just do stuffs on other threads and we want to send a message
self.secret_server = secret_server
self.secret_channel = secret_channel
# a git client linked with the bot github profile
self.git_client = git_client
# the main repo of the bot
self.git_repo = git_repo
# google play api
self.gplay_handler = gplay.GPlay()
```

the things listed can be used to build your classes and stuffs.