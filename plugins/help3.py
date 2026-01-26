from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, mark_plugin_loaded

mark_plugin_loaded("help3.py")

HELP3_TEXT = """
USERBOT HELP 3 (VARS • BOT MANAGER • NEKO)

====================
VARIABLES (VARS)
====================

.setvar <KEY> <VALUE> | exm: .setvar SPAM_BOT_TOKEN 123456:ABC
Save a variable (token / key / value)

.getvar <KEY> | exm: .getvar SPAM_BOT_TOKEN
Get saved variable value

.delvar <KEY> | exm: .delvar SPAM_BOT_TOKEN
Delete a saved variable

.vars | exm: .vars
List all saved variables


====================
BOT MANAGER (MULTI BOT)
====================

.startbot <name> <VAR_KEY> | exm: .startbot spam SPAM_BOT_TOKEN
Start a bot using saved token

.stopbot <name> | exm: .stopbot spam
Stop a running bot

.bots | exm: .bots
Show all running bots


====================
NEKO FUN COMMANDS
====================

.neko | exm: .neko
Random neko image / gif

.nekokiss | exm: .nekokiss
Random neko kiss gif

.nekohug | exm: .nekohug
Random neko hug gif

.nekoslap | exm: .nekoslap
Random neko slap gif

.nekofuck | exm: .nekofuck
Random neko adult gif

• Reply / without reply — both work  
• Media auto deletes after 30 seconds  
• Files picked randomly from assets folder  


====================
ERROR & HEALTH SYSTEM
====================

• Automatic error logging is ENABLED  
• Errors are sent to Saved Messages  
• Plugin health is tracked automatically  

Check broken plugins:
.help broken


====================
NOTES
====================

• All commands are owner-only  
• Vars are stored in data/vars.json  
• Error logs are NOT deleted automatically  
• Key ≠ Bot name  
• Bot name = running bot label  

Example flow:
.setvar SPAM_BOT_TOKEN <token>
.startbot spam SPAM_BOT_TOKEN
"""

@Client.on_message(owner_only & filters.command("help3", "."))
async def help3_cmd(_, m):
    try:
        await m.delete()
    except:
        pass

    msg = await m.reply(HELP3_TEXT)
    await auto_delete(msg, 40)
