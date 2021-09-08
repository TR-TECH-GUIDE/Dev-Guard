import asyncio
import aiohttp
import json
import os
from urllib.parse import urlparse
from pyrogram import Client, filters
from _pyrogram import app, CMD_HELP
from config import PREFIX

CMD_HELP.update(
    {
        "Misc": """
**Misc**
  `paste` -> __Paste replied content to nekobin.com__
  `tr` [lang code] -> __Transalte a text to a given language__
  `info` [user handle] -> __Provides information about the user__
  `id` [user handle] -> __Give user or chat id__
  `restart` -> __Restart the Clients__
  `load -p` -> __To Install/Load Pyrogram Plugins__
  `json` -> __To Get Message Details__
"""
    }
)

TMP_DOWNLOAD_DIRECTORY = "./_pyrogram/"

@app.on_message(filters.command("paste", PREFIX) & filters.me)
async def pastebin(_, message):
    await message.edit("...")
    downloaded_file_name = None

    if message.reply_to_message and message.reply_to_message.media:
        downloaded_file_name_res = await message.reply_to_message.download(
            file_name=TMP_DOWNLOAD_DIRECTORY
        )
        m_list = None
        with open(downloaded_file_name_res, "rb") as fd:
            m_list = fd.readlines()
        downloaded_file_name = ""
        for m in m_list:
            downloaded_file_name += m.decode("UTF-8")
        os.remove(downloaded_file_name_res)
    elif message.reply_to_message:
        downloaded_file_name = message.reply_to_message.text.html
    # elif len(message.command) > 1:
    #     downloaded_file_name = " ".join(message.command[1:])
    else:
        await message.edit("Not said What to do")
        return

    if downloaded_file_name is None:
        await message.edit("Didn't say what to do")
        return

    json_paste_data = {
        "content": downloaded_file_name
    }

    # a dictionary to store different pastebin URIs
    paste_bin_store_s = {
        "deldog": "https://del.dog/documents",
        "nekobin": "https://nekobin.com/api/documents"
    }

    chosen_store = "nekobin"
    if len(message.command) == 2:
        chosen_store = message.command[1]

    # get the required pastebin URI
    paste_store_url = paste_bin_store_s.get(
        chosen_store,
        paste_bin_store_s["nekobin"]
    )
    paste_store_base_url_rp = urlparse(paste_store_url)

    # the pastebin sites, respond with only the "key"
    # we need to prepend the BASE_URL of the appropriate site
    paste_store_base_url = paste_store_base_url_rp.scheme + "://" + \
        paste_store_base_url_rp.netloc

    async with aiohttp.ClientSession() as session:
        response_d = await session.post(paste_store_url, json=json_paste_data)
        response_jn = await response_d.json()

    # we got the response from a specific site,
    # this dictionary needs to be scrapped
    # using bleck megick to find the "key"
    t_w_attempt = bleck_megick(response_jn)
    required_url = json.dumps(
        t_w_attempt, sort_keys=True, indent=4
    ) + "\n\n #ERROR"
    if t_w_attempt is not None:
        required_url = "**Patsted to Nekobin**\n" + paste_store_base_url + "/" + "raw" + "/" + t_w_attempt

    await message.edit(required_url)


def bleck_megick(dict_rspns):
    # first, try getting "key", dirctly
    first_key_r = dict_rspns.get("key")
    # this is for the "del.dog" site
    if first_key_r is not None:
        return first_key_r
    check_if_result_ests = dict_rspns.get("result")
    if check_if_result_ests is not None:
        # this is for the "nekobin.com" site
        second_key_a = check_if_result_ests.get("key")
        if second_key_a is not None:
            return second_key_a
    # TODO: is there a better way?
    return None
