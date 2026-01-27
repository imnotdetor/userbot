from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, get_plugin_health, log_error, mark_plugin_loaded

mark_plugin_loaded("help.py")

# =====================
# SHORT HELP (.help)
# =====================
HELP_SHORT = """
USERBOT HELP

Use:
.help all

Available plugins:
basic
cleanup
spam
forward
media
games
fun
random
auto
mention
vars
info
"""

# =====================
# FULL HELP (.help all)
# =====================
HELP_FULL = """
====================
BASIC
====================
.alive | exm: .alive
Check if userbot is running

.ping | exm: .ping
Check response speed

.restart | exm: .restart
Restart the userbot

====================
CLEANUP
====================
.purge | exm: .purge (reply)
Delete messages from replied msg to command

.clean | exm: .clean (count)
Delete last X messages

.del | exm: .del (reply)
Delete single message

.delall | exm: .delall (reply user)
Delete all messages of a user

====================
SPAM
====================
.spam | exm: .spam (count) (text)
Send same message multiple times

.delayspam | exm: .delayspam (count) (delay) (text)
Spam with delay between messages

.replyspam | exm: .replyspam (count)
Spam reply to a message

====================
FORWARD
====================
.fwd | exm: .fwd (chat_id)
Forward replied message

.sfwd | exm: .sfwd (chat_id)
Silent forward

.fwdhere | exm: .fwdhere (reply)
Forward message to same chat

.mfwd | exm: .mfwd (chat_id) (count)
Forward multiple messages

====================
MEDIA
====================
.ss | exm: .ss (reply view-once)
Save view-once media

.save | exm: .save (reply media)
Save media to Saved Messages

====================
GAMES
====================
.dice  → Roll dice
.coin  → Head / Tail
.luck  → Luck percentage
.rate  → Rate yourself
.roll  → Random number

====================
FUN
====================
.slap | exm: .slap (reply / mention)
Send slap reaction

.hug | exm: .hug (reply / mention)
Send hug reaction

.kiss | exm: .kiss (reply / mention)
Send kiss reaction

.poke | exm: .poke (reply / mention)
Poke someone

.tickle | exm: .tickle (reply / mention)
Tickle reaction

====================
RANDOM
====================
.predict | exm: .predict
Predict something randomly

.8ball | exm: .8ball
Magic 8-ball answers

.truth | exm: .truth
Truth question

.dare | exm: .dare
Dare challenge

.joke | exm: .joke
Random joke

.quote | exm: .quote
Random quote

.insult | exm: .insult (user)
Insult someone (fun)

.compliment | exm: .compliment (user)
Compliment someone

====================
AUTO REPLY
====================
.autoreply on/off
Enable or disable auto reply

.autoreplydelay (seconds)
Set reply delay

.setmorning (text)
.setafternoon (text)
.setevening (text)
.setnight (text)

.awhitelist | exm: (reply)
Allow auto reply to user

.ablacklist | exm: (reply)
Block auto reply for user

====================
VARS
====================
.setvar | exm: .setvar KEY VALUE
Save variable

.getvar | exm: .getvar KEY
Get variable

.delvar | exm: .delvar KEY
Delete variable

.vars
List all variables

====================
INFO
====================
.id
Get IDs

.stats
Account statistics

====================
EXTRA
====================
.help broken
Show broken plugins
"""

# =====================
# HELP HANDLER
# =====================
@Client.on_message(owner_only & filters.command("help", "."))
async def help_cmd(client, m):
    try:
        await m.delete()

        if len(m.command) == 1:
            msg = await m.reply(HELP_SHORT)
            await auto_delete(msg, 30)
            return

        arg = m.command[1].lower()

        if arg == "all":
            msg = await m.reply(HELP_FULL)
            await auto_delete(msg, 90)
            return

        if arg == "broken":
            health = get_plugin_health()
            broken = []

            for p, info in health.items():
                if info.get("last_error"):
                    broken.append(
                        f"{p}\nError: {info['last_error']}\nTime: {info['last_error_time']}"
                    )

            msg = await m.reply(
                "All plugins working ✅"
                if not broken else
                "BROKEN PLUGINS\n\n" + "\n\n".join(broken)
            )
            await auto_delete(msg, 20)

    except Exception as e:
        await log_error(client, "help.py", e)
