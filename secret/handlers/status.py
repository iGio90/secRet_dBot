from datetime import datetime, timedelta


class Status(object):
    def __init__(self, secret_context):
        self.secret_context = secret_context

        # start time
        self.start_time = datetime.now().timestamp()

        # bot status icon
        self.bot_status_icon = "https://upload.wikimedia.org/wikipedia/commons/" \
                               "thumb/3/30/Icons8_flat_clock.svg/2000px-Icons8_flat_clock.svg.png"
        # discord status icon
        self.discord_status_icon = "https://png.icons8.com/color/540/overwolf.png"
        # git status icon
        self.git_status_icon = "https://avatars3.githubusercontent.com/u/1153419?s=400&v=4"
        # mongo status icon
        self.mongo_status_icon = "https://www.todobackend.com/images/logos/mongodb.png"

    def get_bot_status(self):
        datetime_now = datetime.now()
        now = '{0:%H:%M:%S}'.format(datetime_now)
        uptime = str(timedelta(seconds=int(datetime_now.timestamp() - self.start_time)))
        return {
            'now': now,
            'uptime': uptime,
            'icon': self.bot_status_icon
        }

    def get_discord_status(self):
        status = {'connected': self.secret_context.discord_client.is_logged_in,
                  'icon': self.discord_status_icon}
        if status['connected']:
            for server in self.secret_context.discord_client.servers:
                created = '{0:%Y-%m-%d %H:%M:%S}'.format(server.created_at)
                status['id'] = server.id
                status['name'] = server.name
                status['members'] = len(server.members)
                status['created_at'] = created
                break
        return status

    def get_mongo_status(self):
        mongo_status = self.secret_context.mongo_db.command("serverStatus")
        db_stats = self.secret_context.mongo_db.command("dbStats")
        return {
            'host': mongo_status['host'],
            'version': mongo_status['version'],
            'process': mongo_status['process'],
            'pid': mongo_status['pid'],
            'db': db_stats['db'],
            'collections': db_stats['collections'],
            'objects': db_stats['objects'],
            'indexes': db_stats['indexes'],
            'storage_size': db_stats['storageSize'],
            'index_size': db_stats['indexSize'],
            'icon': self.mongo_status_icon
        }

    def get_git_status(self):
        status = self.secret_context.git_client.get_api_status()
        updated = '{0:%Y-%m-%d %H:%M:%S}'.format(status.last_updated)
        return {
            'updated': updated,
            'status': status.status,
            'icon': self.git_status_icon
        }

    def get_status(self):
        return {
            'bot_status': self.get_bot_status(),
            'discord_status': self.get_discord_status(),
            'git_status': self.get_git_status(),
            'mongo_status': self.get_mongo_status()
        }
