import requests


async def on_message(message, discord_client, mongo_db, bus, git_client, git_repo):
    parts = message.content.split(" ")
    if len(parts) > 1:
        cmd = None
        sub = str(parts[1])
        if sub.startswith('http'):
            file_url = parts[1]
            r = requests.get(file_url)
            if r.status_code == 200:
                cmd = r.content.decode('utf8')
        elif sub.startswith("```"):
            cmd = str.join(' ', parts[2:])
            cmd = cmd.replace('```', '')
        if cmd is not None:
            exec(cmd)
            await run(message=message, discord_client=discord_client, mongo_db=mongo_db,
                      bus=bus, git_client=git_client, git_repo=git_repo)
