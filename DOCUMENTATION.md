# Documentation

### Something running that you can access for code your stuffs:
* discord (http://discordpy.readthedocs.io/en/latest/api.html)
* github (http://pygithub.readthedocs.io/en/latest/github.html)
* mongo db (http://docs.mongoengine.org/apireference.html)
* http server and restful api

A lot of things are just not exposed by design (I.E wikipedia api, weather).
This mean, that we have them inside but not exposed. References could be created as needed!


---

### Add commands and features
1) add your command to the commands map ``discord_commands/map/user_commands.json``
2) eventually, add a shortcut for it ``discord_commands/map/shortcuts.json``
3) code the root handler in ``secret/message_handler.py``

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

If you like to code advanced and more complex stuffs, you can add your classes to ``discord_commands/`` package.
A little example from ``secret/message_handler.py``:

```python
async def wikipedia(self, message):
    await wikipedia.on_message(message, self.discord_client, self.bus)
```

---

### Give your classes something to use from the secret context

I think there is no need of so much description if you are arrived here.
The ``secret_context`` is/can be shared to any additional module and hold a reference
of anything that can be used

```python
# event bus and loop
self.main_loop = asyncio.get_event_loop()
self.bus = EventBus()

# mongo db free4all
connect('secret')
self.mongo_db = Document._get_db()

# discord
self.discord_client = discord.Client()
self.secret_server = discord.Server(id='326095959173890059')
self.secret_channel = discord.Channel(id='404630967257530372',
                                      server=self.secret_server)
self.welcome_channel = discord.Channel(id='404795628019777557',
                                       server=self.secret_server)

# github
self.git_client = Github(configs['github_username'], configs['github_password'])
self.git_repo = self.git_client.get_repo('secRetDBot/secRet_dBot')

# discord message handler
self.message_handler = MessageHandler(self)

# handlers
self.handler_status = status.Status(self.mongo_db, self.git_client)
```

the things listed can be used to build your classes and stuffs.

## Develop and test
To develop and test your stuff I believe you can just create a test.py and implement it as a command,
however, you may want to try some cool api from discord and so you can use the ``samples/``.