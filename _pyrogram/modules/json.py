from pyrogram.types import *
from _pyrogram import *
from pyrogram import *
from config import *
from os import *

@app.on_message(filters.command("json", PREFIX) & filters.me)
async def start(client, message):
    try:
        if message.reply_to_message:
            msg = message.reply_to_message

        else:
            msg = message

        msg_info = str(msg)

        if len(msg_info) > int("4096"):
            file = open("json.txt", "w+")
            file.write(msg_info)
            file.close()
            await app.send_document(
                message.chat.id,
                "json.txt",
                caption="Returned JSon",

            )
            remove("json.txt")

        else:
            await message.edit(msg_info)

    except Exception as e:
        await message.edit(f"{e}")
