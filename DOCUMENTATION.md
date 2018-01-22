## Documentation

Adding command and features it's very easy. The file you need to check to start with is message_handler.
The commands map are pretty easy to understand and will let you add your commands handlers.
The main function invoked by yours handler MUST be coded inside the message handler.
If your functions is very short and take a couple of lines, it's good to code it straight on message_handler, otherwise I suggest to create and import your own files and follow your flows there.
A little example:
```
"commits": {
        "author": "iGio90",
        "description": "last 10 commits on secRet repo",
        "function": "commits"
    }
```
Note: function must be ``async``. message object hold everything (sender, reactions etc etc)
```
async def commits(self, message):
    """
    list last 10 commits in the repo
    """
    commits_embed = commands_git.build_commit_list_embed(self.git_repo)
    await self.client.send_message(message.channel, embed=commits_embed)
```

Refer also to the Discord bot documentation for interacting with all the objects it provides:
http://discordpy.readthedocs.io/en/latest/api.html#

## Additional
The bot runs an hourly task on a separate thread which can be used to do additional stuffs.
secret.py does the job and you can add an eventual hourly task here as well:
```
def secret_hourly_task(self):
    # add your stuffs
```

To send messages from this thread we must use an event bus instead.

Send message from the main thread
```
await self.client.send_message(message.channel, embed=commits_embed)
```

Send a message from secret thread (event bus):
```
def ding(self):
    now = datetime.now()
    s = ''
    for i in range(0, now.hour):
        s += 'DING '
    self.bus.emit('secret_send', message=s)
```

## Api

TODO