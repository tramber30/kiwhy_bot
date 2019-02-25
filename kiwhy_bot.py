#!/usr/bin/env python3
"""
 Copyright (C) 2019  Nicolas Bertrand

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import discord
import asyncio
import json 
import time
import datetime

class KiwhyClient(discord.Client):
    async def on_ready(self):
        print("logged in as")
        print(self.user.name)
        print(self.user.id)
        print("----------")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith("!history"):
            counter = 0
            tmp = await message.channel.send("Calculating...")
            async for msg in message.channel.history(limit=100):
                if message.author in msg.mentions:
                    counter += 1
            await tmp.edit(content='You are mentioned {} times in history.'.format(counter))
        elif message.content.startswith("!clean"):
            if message.channel.name == "notifications":
                await message.channel.purge(limit=100)
            else:
                await message.channel.send("command only available in notifications chan")

    async def on_member_update(self, before, current):
        if current.status == discord.Status.online and (before.status == discord.Status.offline or before.status == discord.Status.invisible):
            print("member [%s] is now online" % current)
            notif_chan = [chan for chan in current.guild.text_channels if chan.name == "notifications"]
            if len(notif_chan) < 1:
                print ("no notification channel")
            for chan in current.guild.text_channels:
                if chan.name == "notifications":
                    await chan.send("[%d:%d] member %s is now online" % (time.localtime().tm_hour, time.localtime().tm_min, current.mention))
        if current.status == discord.Status.offline and before.status != discord.Status.offline:
            print("member [%s] is now offline" % current)
            for chan in current.guild.text_channels:
                if chan.name == "notifications":
                    current_time = time.gmtime()
                    hour_back = range(0,24)[current_time.tm_hour - 8]
                    time_limit = datetime.datetime(current_time.tm_year, current_time.tm_mon, current_time.tm_mday, hour_back, current_time.tm_min)
                    async for msg in chan.history(limit=50, after=time_limit, reverse=False):
                        if current in msg.mentions:
                            updated_content =  '{}\n[{}:{}] member {} is now offline'.format(msg.content, time.localtime().tm_hour, time.localtime().tm_min, current.mention)
                            await msg.edit(content=updated_content)
                            break

if __name__ == "__main__":
    try:                
        credentials = json.loads(open("credentials.json", "r").read())
    except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
        print("Error reading credentials: {}\nExiting...".format(str(err)))
        exit(1)

    client = KiwhyClient()
    res = client.run(credentials["bot-token"])
    print('return value: (%d)' % res)
