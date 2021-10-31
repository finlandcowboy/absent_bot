import discord
from discord.ext import tasks, commands
from config import settings
import datetime
import database

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        self.channel = settings['ADMIN_CHANNEL_ID']
        self.missing_users = database.get_users()
        self.all_users = database.get_users()
        super().__init__(*args, **kwargs)
        self.check_active_users.start()

    async def on_ready(self):
        print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
        print(f'| Logged in as {self.user.name} {self.user.id} |')
        print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
        members = []
        for guild in self.guilds:
            print('Guild member:', guild.members, '\n\n')
            for member in guild.members:
                m = {}
                if not member.bot:
                    print('Member:', member)
                    if member.nick:
                        m['name'] = member.nick
                    else:
                        m['name'] = member.name
                    m['last_seen'] = datetime.datetime.now().strftime(settings['DATETIME_FORMAT'])
                    members.append(m)
        print("Members:", members)
        database.fill_users_table(members)

    @tasks.loop(seconds=3.0)
    async def check_active_users(self):
        self.missing_users = database.get_users()
        print('Missing_users', self.missing_users)
        active_users = []
        for guild in self.guilds:
            for voice_channel in guild.voice_channels:
                active_users += voice_channel.members

        returned_users = [user for user in active_users if user.name in [x['name'] for x in self.missing_users]]
        # TODO: Сделать расчет времени отсутствия пользователя (посмотреть какой тип данных будет в sqlite3)

        msg  = ''
        print('Active users', active_users)
        print('Returned users', returned_users)
        for user in self.missing_users:
            if user['name'] in [member.name for member in returned_users]:
                print(f"User {user['name']} has returned")
                time_delta = datetime.datetime.now() - datetime.datetime.strptime(user['last_seen'], settings['DATETIME_FORMAT'])
                if time_delta.seconds // 60 > 1:
                    msg += f"User: {user['name']} was absent for {time_delta.seconds // 60} mins"
                user_data = {
                    'name' : user['name'],
                    'last_seen' : datetime.datetime.now().strftime(settings['DATETIME_FORMAT'])
                }
                database.update_last_seen(user_data)

        print('Message', msg)

        admin_channel = self.get_channel(self.channel)
        if len(msg):
            await admin_channel.send(msg)

        # TODO: Добавить запись когда пользак вернулся и когда отсутствовал (name, last_seen, connected_at, role)
        # ! Чтобы по ролям можно было в конце дня делать отчет кто и когда отсутствовал 

    @check_active_users.before_loop
    async def check_if_ready(self):
        await self.wait_until_ready()
        print('Checking active users...')


if __name__ == '__main__':
    database.on_login()
    intents = discord.Intents.all()
    bot = MyClient(intents=intents, fetch_offline_members=True, heartbeat_timeout=15, guild_subscriptions=True)
    bot.run(settings["TOKEN"])
