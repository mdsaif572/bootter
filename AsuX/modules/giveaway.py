import os
from asyncio import sleep
from datetime import datetime, timedelta
from random import choice
from traceback import format_exc

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType as CT
from pyrogram.enums import MessageMediaType as MMT
from pyrogram.errors import UserNotParticipant
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from AsuX import LOGGER, Abishnoi
from AsuX.db.giveaway_db import GIVEAWAY

GA = GIVEAWAY()


user_entry = {}  # {c_id :  {participants_id : 0}}} dict be like
voted_user = {}  # {c_id : [voter_ids]}} dict be like
total_entries = {}  # {c_id : [user_id]} dict be like for participants
left_deduct = (
    {}
)  # {c_id:{u_id:p_id}} u_id = user who have voted, p_id = participant id. Will deduct vote from participants account if user leaves
rejoin_try = (
    {}
)  # store the id of the user who lefts the chat while giveaway under-process {c_id:[]}
is_start_vote = []  # store id of chat where voting is started


@Abishnoi.on_cmd(["startgiveaway", "startga"], pm_only=True)
async def start_give_one(c: Abishnoi, m: Message):
    uWu = True
    try:
        if m.chat.type != CT.PRIVATE:
            await m.reply_text("**ᴜsᴀɢᴇ**\n/startgiveaway\nᴍᴇᴀɴᴛ ᴛᴏ ʙᴇ ᴜsᴇᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ")
            return
        g_id = await c.ask(
            text="sᴇɴᴅ ᴍᴇ ɴᴜᴍʙᴇʀ ᴏғ ɢɪᴠᴇᴀᴡᴀʏ", chat_id=m.chat.id, filters=filters.text
        )
        give_id = g_id.text.markdown
        curr = GA.give_info(u_id=m.from_user.id)
        if curr:
            gc_id = curr["chat_id"]
            c_id = curr["where"]
            if curr["is_give"]:
                await m.reply_text("ᴏɴᴇ ɢɪᴠᴇᴀᴡᴀʏ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss")
                return
            while True:
                con = await c.ask(
                    text="ʏᴏᴜ ɪɴғᴏ ɪs ᴀʟʀᴇᴀᴅʏ ᴘʀᴇsᴇɴᴛ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ\nʏᴇs : ᴛᴏ sᴛᴀʀᴛ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ ᴡɪᴛʜ ᴘʀᴇᴠɪᴏᴜs ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴs\nɴᴏ: ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴏɴᴇ",
                    chat_id=m.chat.id,
                    filters=filters.text,
                )
                if con.text.lower() == "/cancel":
                    await m.reply_text("ᴄᴀɴᴄᴇʟʟᴇᴅ")
                    return
                if con.text.lower() == "yes":
                    await c.send_message(m.chat.id, "ᴅᴏɴᴇ")
                    while True:
                        yes_no = await c.ask(
                            text="ᴏᴋ.\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀʟʟᴏᴡ ᴏʟᴅ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴄᴀɴ ᴠᴏᴛᴇ ɪɴ ᴛʜɪs ɢɪᴠᴇᴀᴡᴀʏ.\n**ʏᴇs: ᴛᴏ ᴀʟʟᴏᴡ**\n**ɴᴏ: ᴛᴏ ᴅᴏɴ'ᴛ ᴀʟʟᴏᴡ**\nɴᴏᴛᴇ ᴛʜᴀᴛ ᴏʟᴅ ᴍᴇᴀɴ ᴜsᴇʀ ᴡʜᴏ ɪs ᴘʀᴇsᴇɴᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ғᴏʀ ᴍᴏʀᴇ ᴛʜᴀɴ 48 ʜᴏᴜʀs",
                            chat_id=m.from_user.id,
                            filters=filters.text,
                        )
                        if yes_no.text.lower() == "/cancel":
                            await m.reply_text("ᴄᴀɴᴄᴇʟʟᴇᴅ")
                            return
                        if yes_no.text.lower() == "yes":
                            is_old = 0
                            break
                        elif yes_no.text.lower() == "no":
                            is_old = 1
                            break
                        else:
                            await c.send_message(m.chat.id, "ᴛʏᴘᴇ ʏᴇs ᴏʀ ɴᴏ ᴏɴʟʏ")
                    f_c_id = gc_id
                    s_c_id = c_id
                    is_old = is_old
                    GA.update_is_old(m.from_user.id, is_old)
                    GA.stop_entries(m.from_user.id, entries=1)  # To start entries
                    GA.stop_give(m.from_user.id, is_give=1)  # To start giveaway
                    link = await c.export_chat_invite_link(s_c_id)
                    uWu = False
                    await c.send_message(m.chat.id, "ᴅᴏɴᴇ")
                    break
                elif con.text.lower() == "no":
                    uWu = True
                    break
                else:
                    await c.send_message(m.chat.id, "ᴛʏᴘᴇ ʏᴇs ᴏʀ ɴᴏ ᴏɴʟʏ")
        if uWu:
            while True:
                channel_id = await c.ask(
                    text="ᴏᴋ....sᴇɴᴅ ᴍᴇ ɪᴅ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ ɪ ᴀᴍ ᴀᴅᴍɪɴ ᴛʜᴇɪʀ. ɪғ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ɪᴅ ғᴏʀᴡᴀʀᴅ ᴀ ᴘᴏsᴛ ғʀᴏᴍ ʏᴏᴜʀ ᴄʜᴀᴛ.\nᴛʏᴘᴇ /cancel ᴄᴀɴᴄᴇʟ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʀᴏᴄᴇss",
                    chat_id=m.chat.id,
                    filters=filters.text,
                )
                if channel_id.text:
                    if str(channel_id.text).lower() == "/cancel":
                        await c.send_message(m.from_user.id, "ᴄᴀɴᴄᴇʟʟᴇᴅ")
                        return
                    try:
                        c_id = int(channel_id.text)
                        try:
                            bot_stat = (
                                await c.get_chat_member(c_id, Abishnoi.id)
                            ).status
                            if bot_stat in [CMS.ADMINISTRATOR, CMS.OWNER]:
                                break
                            else:
                                await c.send_message(
                                    m.chat.id,
                                    f"ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ {c_id}\nᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʜᴇɴ sᴇɴᴅ ᴍᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀɢᴀɪɴ",
                                )
                        except UserNotParticipant:
                            await c.send_message(
                                m.chat.id,
                                f"ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴀᴍ ɴᴏᴛ ᴘᴀʀᴛ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ {c_id}\n",
                            )

                    except ValueError:
                        await c.send_message(
                            m.chat.id, "ᴄʜᴀɴɴᴇʟ ɪᴅ sʜᴏᴜʟᴅ ʙᴇ ɪɴᴛᴇɢᴇʀ ᴛʏᴘᴇ"
                        )

                else:
                    if channel_id.forward_from_chat:
                        try:
                            bot_stat = (
                                await c.get_chat_member(c_id, Abishnoi.id)
                            ).status
                            if bot_stat in [CMS.ADMINISTRATOR, CMS.OWNER]:
                                break
                            else:
                                await c.send_message(
                                    m.chat.id,
                                    f"ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ {c_id}\nᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʜᴇɴ sᴇɴᴅ ᴍᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀɢᴀɪɴ",
                                )
                        except UserNotParticipant:
                            await c.send_message(
                                m.chat.id,
                                f"ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴀᴍ ɴᴏᴛ ᴘᴀʀᴛ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ {c_id}\n",
                            )
                    else:
                        await c.send_message(
                            m.chat.id,
                            f"ғᴏʀᴡᴀʀᴅ ᴍᴇ ᴄᴏɴᴛᴇɴᴛ ғʀᴏᴍ ᴄʜᴀᴛ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴛᴀʀᴛ ɢɪᴠᴇᴀᴡᴀʏ",
                        )
            f_c_id = c_id
            await c.send_message(m.chat.id, "ᴄʜᴀɴɴᴇʟ ɪᴅ ʀᴇᴄᴇɪᴠᴇᴅ")
            while True:
                chat_id = await c.ask(
                    text="sᴇɴᴅᴇ ᴍᴇ ɪᴅ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ ɪ ᴀᴍ ᴀᴅᴍɪɴ ᴛʜᴇɪʀ. ɪғ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ɪᴅ ɢᴏ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ᴛʏᴘᴇ /id.\nᴛʏᴘᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʀᴏᴄᴇss",
                    chat_id=m.chat.id,
                    filters=filters.text,
                )
                if chat_id.text:
                    if str(chat_id.text).lower() == "/cancel":
                        await c.send_message(m.from_user.id, "ᴄᴀɴᴄᴇʟʟᴇᴅ")
                        return
                    try:
                        cc_id = int(chat_id.text)
                        try:
                            cc_id = (await c.get_chat(cc_id)).id
                            s_c_id = cc_id
                            break
                        except Exception:
                            try:
                                cc_id = await c.resolve_peer(cc_id)
                                cc_id = (await c.get_chat(cc_id.channel_id)).id
                                s_c_id = cc_id
                                break
                            except Exception as e:
                                await c.send_message(
                                    m.chat.id, f"ʟᴏᴏᴋs ʟɪᴋᴇ ᴄʜᴀᴛ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ: {e}"
                                )
                    except ValueError:
                        await c.send_message(
                            m.chat.id, "ᴄʜᴀᴛ ɪᴅ sʜᴏᴜʟᴅ ʙᴇ ɪɴᴛᴇɢᴇʀ ᴛʏᴘᴇ"
                        )
                    try:
                        bot_stat = (await c.get_chat_member(s_c_id, Abishnoi.id)).status
                        if bot_stat in [CMS.ADMINISTRATOR, CMS.OWNER]:
                            break
                        else:
                            await c.send_message(
                                m.chat.id,
                                f"ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ {s_c_id}\nᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʜᴇɴ sᴇɴᴅ ᴍᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀɢᴀɪɴ",
                            )
                    except UserNotParticipant:
                        await c.send_message(
                            m.chat.id,
                            f"ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴀᴍ ɴᴏᴛ ᴘᴀʀᴛ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ {s_c_id}\n",
                        )

            await c.send_message(m.chat.id, "ᴄʜᴀᴛ ɪᴅ ʀᴇᴄᴇɪᴠᴇᴅ")

            link = await c.export_chat_invite_link(cc_id)

            yes_no = await c.ask(
                text="ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀʟʟᴏᴡ ᴏʟᴅ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴄᴀɴ ᴠᴏᴛᴇ ɪɴ ᴛʜɪs ɢɪᴠᴇᴀᴡᴀʏ.\n**ʏᴇs: ᴛᴏ ᴀʟʟᴏᴡ**\n**ɴᴏ: ᴛᴏ ᴅᴏɴ'ᴛ ᴀʟʟᴏᴡ**\nɴᴏᴛᴡ ᴛʜᴀᴛ ᴏʟᴅ ᴍᴇᴀɴ user ᴡʜᴏ ɪs ᴘʀᴇsᴇɴᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ғᴏʀ ᴍᴏʀᴇ ᴛʜᴀɴ 48 ʜᴏᴜʀs",
                chat_id=m.from_user.id,
                filters=filters.text,
            )
            if yes_no.text.lower() == "yes":
                is_old = 0
            elif yes_no.text.lower() == "no":
                is_old = 1
            curr = GA.save_give(f_c_id, s_c_id, m.from_user.id, is_old, force_c=True)
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

    reply = m.reply_to_message
    giveaway_text = f"""
**#ɢɪᴠᴇᴀᴡᴀʏ {give_id} 》**
➖➖➖➖➖➖➖➖➖➖➖
__ᴛᴏ ᴡɪɴ ᴛʜɪs ɢɪᴠᴇᴀᴡᴀʏ__
__ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ ᴛʜᴇ ᴄᴏɴᴛᴇsᴛ__,
__ᴄᴏᴍᴍᴇɴᴛ /enter ᴛᴏ ʙᴇɢɪɴ__

ʙᴏᴛ sʜᴏᴜʟᴅ ʙᴇ sᴛᴀʀᴛᴇᴅ!
➖➖➖➖➖➖➖➖➖➖➖
**sᴛᴀᴛᴜs : ᴇɴᴛʀɪᴇs ᴏᴘᴇɴ**
"""

    kb = IKM(
        [
            [IKB("ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀᴛ", url=link)],
            [IKB("sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ", url=f"https://{Abishnoi.username}.t.me/")],
        ]
    )
    try:
        if reply and (
            reply.media in [MMT.VIDEO, MMT.PHOTO]
            or (reply.document.mime_type.split("/")[0] == "image")
        ):
            if reply.photo:
                pin = await c.send_photo(
                    f_c_id, reply.photo.file_id, giveaway_text, reply_markup=kb
                )
            elif reply.video:
                pin = await c.send_video(
                    f_c_id, reply.video.file_id, giveaway_text, reply_markup=kb
                )
            elif reply.document:
                download = await reply.download()
                pin = await c.send_photo(
                    f_c_id, download, giveaway_text, reply_markup=kb
                )
                os.remove(download)
        else:
            pin = await c.send_message(
                f_c_id, giveaway_text, reply_markup=kb, disable_web_page_preview=True
            )
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        await m.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ᴄʜᴀɴɴᴇʟ ᴅᴜᴇ ᴛᴏ\n{e}")
        return
    c_in = await c.get_chat(f_c_id)
    name = c_in.title
    await m.reply_text(
        f"✨ ɢɪᴠᴇᴀᴡᴀʏ ᴘᴏsᴛ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ [{name}]({c_in.invite_link})",
        disable_web_page_preview=True,
        reply_markup=IKM([[IKB("ɢᴏ ᴛᴏ ᴘᴏsᴛ", url=pin.link)]]),
    )


async def message_editor(c: Abishnoi, m: Message, c_id):
    txt = f"""
**#ɢɪᴠᴇᴀᴡᴀʏ 》**
➖➖➖➖➖➖➖➖➖➖➖
__ᴛᴏ ᴡɪɴ ᴛʜɪs ɢɪᴠᴇᴀᴡᴀʏ__
__ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ ᴛʜᴇ ᴄᴏɴᴛᴇsᴛ__,
__ᴄᴏᴍᴍᴇɴᴛ /enter ᴛᴏ ʙᴇɢɪɴ__

ɴᴏᴛᴇ: ʙᴏᴛ sʜᴏᴜʟᴅ ʙᴇ sᴛᴀʀᴛᴇᴅ !
➖➖➖➖➖➖➖➖➖➖➖
**sᴛᴀᴛᴜs : ᴇɴᴛʀɪᴇs ᴄʟᴏsᴇᴅ**
**ᴛᴏᴛᴀʟ ᴇɴᴛʀɪᴇs : {len(total_entries[c_id])}**
"""
    try:
        m_id = int(m.text.split(None)[1].split("/")[-1])
    except ValueError:
        await m.reply_text("ᴛʜᴇ ʟɪɴᴋ ᴅᴏᴇsɴ'ᴛ ᴄᴏɴᴛᴀɪɴ ᴀɴʏ ᴍᴇssᴀɢᴇ ɪᴅ")
        return False
    try:
        mess = await c.get_messages(c_id, m_id)
    except Exception as e:
        await m.reply_text(
            f"ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴍᴇssᴀɢᴇ ғᴏʀᴍ ᴛʜᴇ ᴄʜᴀᴛ ɪᴅ {c_id}. ᴅᴜᴇ ᴛᴏ ғᴏʟʟᴏᴡɪɴɢ ᴇʀʀᴏʀ\n{e}"
        )
        return False
    try:
        if mess.caption:
            await mess.edit_caption(txt)
        else:
            await mess.edit_text(txt)
        return True
    except Exception as e:
        await m.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴅᴜᴇ ᴛᴏ ғᴏʟʟᴏᴡɪɴɢ ᴇʀʀᴏʀ\n{e}")
        await m.reply_text(
            f"ʜᴇʀᴇ ɪs ᴛʜᴇ ᴛᴇxᴛ ʏᴏᴜ ᴄᴀɴ ᴇᴅɪᴛ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʙʏ ʏᴏᴜʀ sᴇʟғ\n`{txt}`\nsᴏʀʀʏ ғᴏʀ ɪɴᴄᴏɴᴠᴇɴɪᴇɴᴄᴇ"
        )
        return False


@Abishnoi.on_cmd("stopentry")
async def stop_give_entry(c: Abishnoi, m: Message):
    u_id = m.from_user.id
    curr = GA.give_info(u_id=u_id)
    if not curr:
        await m.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀɴʏ ɢɪᴠᴇᴀᴡᴀʏ ʏᴇᴀᴛ.")
        return
    if not curr["entries"]:
        await m.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀɴʏ ɢɪᴠᴇᴀᴡᴀʏ ʏᴇᴀᴛ.")
        return
    user = curr["user_id"]
    if u_id != user:
        await m.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴛʜᴇ ᴏɴᴇ ᴡʜᴏ ʜᴀᴠᴇ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
        return
    c_id = curr["chat_id"]
    if len(m.text.split(None)) != 2:
        await m.reply_text("**ᴜsᴀɢᴇ**\n`/stopentry <ᴘᴏsᴛ ʟɪɴᴋ>`")
        return
    GA.stop_entries(u_id)
    z = await message_editor(c, m, c_id)
    if not z:
        return
    await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ғᴜʀᴛʜᴇʀ ᴇɴᴛʀɪᴇs")
    return


def clean_values(c_id):
    try:
        rejoin_try[c_id].clear()
    except KeyError:
        pass
    try:
        user_entry[c_id].clear()
    except KeyError:
        pass
    try:
        left_deduct[c_id].clear()
    except KeyError:
        pass
    try:
        total_entries[c_id].clear()
    except KeyError:
        pass
    try:
        is_start_vote.remove(c_id)
    except ValueError:
        pass
    try:
        voted_user[c_id].clear()
    except KeyError:
        pass
    return


@Abishnoi.on_cmd(["stopgiveaway", "stopga"])
async def stop_give_away(c: Abishnoi, m: Message):
    u_id = m.from_user.id
    curr = GA.give_info(u_id=u_id)
    if not curr:
        await m.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀɴʏ ɢɪᴠᴇᴀᴡᴀʏ ʏᴇᴛ")
        return
    if not curr["is_give"]:
        await m.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀɴʏ ɢɪᴠᴇᴀᴡᴀʏ ʏᴇᴛ")
        return
    user = curr["user_id"]
    c_id = curr["chat_id"]

    GA.stop_entries(u_id)
    GA.start_vote(u_id, 0)
    try:
        if not len(total_entries[c_id]):
            await m.reply_text("ɴᴏ ᴇɴᴛɪʀᴇs ғᴏᴜɴᴅ")
            GA.stop_give(u_id)
            clean_values(c_id)
            await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
            return
    except KeyError:
        await m.reply_text("ɴᴏ ᴇɴᴛɪʀᴇs ғᴏᴜɴᴅ")
        GA.stop_give(u_id)
        clean_values(c_id)
        await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
        return
    if u_id != user:
        await m.reply_text("You ᴀʀᴇ ɴᴏᴛ ᴛʜᴇ ᴏɴᴇ ᴡʜᴏ ʜᴀᴠᴇ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
        return
    try:
        if not len(user_entry[c_id]):
            await m.reply_text("ɴᴏ ᴇɴᴛʀɪᴇs ғᴏᴜɴᴅ")
            GA.stop_give(u_id)
            clean_values(c_id)
            await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
            return
    except KeyError:
        GA.stop_give(u_id)
        clean_values(c_id)
        await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
        return
    GA.stop_give(u_id)
    try:
        if not len(voted_user[c_id]):
            clean_values(c_id)
            await m.reply_text("ɴᴏ ᴠᴏᴛᴇʀs ғᴏᴜɴᴅ")
            GA.stop_give(u_id)
            await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
            return
    except KeyError:
        GA.stop_give(u_id)
        clean_values(c_id)
        await m.reply_text("sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
        return
    # highest = max(user_entry[c_id], key=lambda k:user_entry[c_id][k])
    # high = user_entry[c_id][highest]
    max_value = max(user_entry[c_id].values())
    max_user = []
    for k, v in user_entry[c_id].items():
        if v == max_value:
            max_user.append(k)
    if len(max_user) == 1:
        high = max_value
        user_high = (await c.get_users(max_user[0])).mention
        txt = f"""
**ɢɪᴠᴇᴀᴡᴀʏ ᴄᴏᴍᴘʟᴇᴛᴇ** ✅
➖➖➖➖➖➖➖➖➖➖➖
≡ ᴛᴏᴛᴀʟ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛs: {len(total_entries[c_id])}
≡ ᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ of ᴠᴏᴛᴇs: {len(voted_user[c_id])}

≡ ᴡɪɴɴᴇʀ 🏆 : {user_high}
≡ ᴠᴏᴛᴇ ɢᴏᴛ 🗳 : `{high}` ᴠᴏᴛᴇs
➖➖➖➖➖➖➖➖➖➖➖
>>>ᴛʜᴀɴᴋs ғᴏʀ ᴘᴀʀᴛɪᴄɪᴘᴀᴛɪɴɢ
"""
    else:
        to_key = [
            "ᴊᴀɪ ʜɪɴᴅ",
            "ᴊᴀɪ ᴊᴀᴡᴀᴀɴ",
            "ᴊᴀɪ ʙʜᴀʀᴀᴛ",
            "ᴊᴀɪ sʜʀᴇᴇ ʀᴀᴍ",
            "ᴊᴀɪ sʜʀᴇᴇ sʜʏᴀᴍ",
            "ᴊᴀɪ sʜʀᴇᴇ ᴋʀɪsʜɴ",
            "ᴊᴀɪ sʜʀᴇᴇ ʀᴀᴅʜᴇ",
            "ʀᴀᴅʜᴇ ʀᴀᴅʜᴇ",
            "sᴀᴍʙʜᴜ",
            "ᴊᴀɪ ᴍᴀᴛᴀ ᴅɪ",
            "ᴊᴀɪ ᴍᴀʜᴀᴋᴀᴀʟ",
            "ᴊᴀɪ ʙᴀᴊᴀʀᴀɴɢʙᴀʟɪ",
        ]
        key = choice(to_key)
        high = max_value
        user_h = [i.mention for i in await c.get_users(max_user)]
        txt = f"""
**ɢɪᴠᴇᴀᴡᴀʏ ᴄᴏᴍᴘʟᴇᴛᴇ** ✅
➖➖➖➖➖➖➖➖➖➖➖
≡ Total participants: {len(total_entries[c_id])}
≡ ᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ᴠᴏᴛᴇs: {len(voted_user[c_id])}

≡ ɪᴛ's a ᴛɪᴇ ʙᴇᴛᴡᴇᴇɴ ғᴏʟʟᴏᴡɪɴɢ ᴜsᴇʀs:
{", ".join(user_h)}
≡ ᴛʜᴇʏ ᴇᴀᴄʜ ɢᴏᴛ 🗳 : `{high}` ᴠᴏᴛᴇs
➖➖➖➖➖➖➖➖➖➖➖
>>>ᴛʜᴀɴᴋs ғᴏʀ ᴘᴀʀᴛɪᴄɪᴘᴀᴛɪɴɢ

ᴛʜᴇ ᴜsᴇʀ ᴡʜᴏ ᴡɪʟʟ ᴄᴏᴍᴍᴇɴᴛ ᴛʜᴇ ᴄᴏᴅᴇ ᴡɪʟʟ ᴡɪɴ 🙂
ᴄᴏᴅᴇ: `{key}`
"""
    await c.send_message(c_id, txt)
    clean_values(c_id)
    await m.reply_text("sᴛᴏᴘᴘᴇᴅ ɢɪᴠᴇᴀᴡᴀʏ")


@Abishnoi.on_cmd("startvote")
async def start_the_vote(c: Abishnoi, m: Message):
    u_id = m.from_user.id
    curr = GA.give_info(u_id=m.from_user.id)
    if not curr:
        await m.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀɴʏ ɢɪᴠᴇᴀᴡᴀʏ ʏᴇᴛ")
        return
    if not curr["is_give"]:
        await m.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀɴʏ ɢɪᴠᴇᴀᴡᴀʏ ʏᴇᴛ")
        return
    c_id = curr["chat_id"]
    user = curr["user_id"]
    if len(is_start_vote):
        if m.chat.id in is_start_vote:
            await m.reply_text("ᴠᴏᴛɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ")
            return
    if len(m.text.split(None)) == 2:
        await message_editor(c, m, c_id)
    else:
        await m.reply_text("ɴᴏ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ᴘʀᴏᴠɪᴅᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ sᴛᴀᴛᴜs ᴛᴏ ᴄʟᴏsᴇᴅ")
    GA.stop_entries(u_id)
    if u_id != user:
        await m.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴛʜᴇ ᴏɴᴇ ᴡʜᴏ ʜᴀᴠᴇ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
        return
    try:
        if not len(total_entries[c_id]):
            clean_values(c_id)
            await m.reply_text("ɴᴏ ᴇɴᴛɪʀᴇs ғᴏᴜɴᴅ")
            return
    except KeyError:
        clean_values(c_id)
        await m.reply_text("ɴᴏ ᴇɴᴛɪʀᴇs ғᴏᴜɴᴅ")
        return
    users = await c.get_users(total_entries[c_id])
    c_link = await c.export_chat_invite_link(c_id)
    for user in users:
        u_id = user.id
        full_name = user.first_name
        if user.last_name and user.first_name:
            full_name = user.first_name + " " + user.last_name
        u_name = user.username if user.username else user.mention
        txt = f"""
**ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ's ɪɴғᴏ:** 🔍  》
➖➖➖➖➖➖➖➖➖➖➖
≡ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ ɴᴀᴍᴇ : {full_name}
≡ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ ID : `{u_id}`
≡ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ's {'username' if user.username else "mention"} : {'@'if user.username else ""}{u_name}
➖➖➖➖➖➖➖➖➖➖➖
>>>ᴛʜᴀɴᴋs ғᴏʀ ᴘᴀʀᴛɪᴄɪᴘᴀᴛɪɴɢ
"""
        if not len(user_entry):
            user_entry[c_id] = {u_id: 0}
        else:
            try:
                user_entry[c_id][u_id] = 0
            except KeyError:
                user_entry[c_id] = {u_id: 0}
        vote_kb = IKM([[IKB("❤️", f"vote_{c_id}_{u_id}")]])
        um = await c.send_message(c_id, txt, reply_markup=vote_kb)
        if m.chat.username and not c_link:
            c_link = f"https://t.me/{m.chat.username}"
        join_channel_kb = IKM([[IKB("ɢɪᴠᴇᴀᴡᴀʏ ᴄʜᴀɴɴᴇʟ", url=c_link)]])
        txt_ib = f"ᴠᴏᴛɪɴɢ ʜᴀs ʙᴇᴇɴ sᴛᴀʀᴛᴇᴅ 》\n\n>>>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ᴠᴏᴛᴇ ʟɪɴᴋ :\nʜᴇʀᴇ ɪs ʏᴏᴜʀ ᴠᴏᴛᴇ ᴍᴇssᴀɢᴇ ʟɪɴᴋ {um.link}.\n\n**ᴛʜɪɴɢs ᴛᴏ ᴋᴇᴇᴘ ɪɴ ᴍɪɴᴅ**\n■ ɪғ ᴜsᴇʀ ʟᴇᴛ's ᴛʜᴇ ᴄʜᴀᴛ ᴀғᴛᴇʀ ᴠᴏᴛɪɴɢ ʏᴏᴜʀ ᴠᴏᴛᴇ count ᴡɪʟʟ ʙᴇ ᴅᴇᴅᴜᴄᴛᴇᴅ.\n■ ɪғ ᴀɴ ᴜsᴇʀ ʟᴇғᴛ ᴀɴᴅ ʀᴇᴊᴏɪɴs ᴛʜᴇ ᴄʜᴀᴛ ʜᴇ ᴡɪʟʟ ɴᴏᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴠᴏᴛᴇ.\n■ ɪғ ᴀɴ ᴜsᴇʀ ɪs ɴᴏᴛ ᴘᴀʀᴛ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴛʜᴇɴ ʜᴇ'ʟʟ ɴᴏᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴠᴏᴛᴇ"
        await c.send_message(
            u_id, txt_ib, reply_markup=join_channel_kb, disable_web_page_preview=True
        )
        await sleep(3)  # To avoid flood
    GA.start_vote(u_id)
    is_start_vote.append(c_id)
    await m.reply_text("sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ᴠᴏᴛɪɴɢ")
    return


@Abishnoi.on_cmd(["enter", "register", "participate"])
async def register_user(c: Abishnoi, m: Message):
    curr = GA.is_vote(m.chat.id)
    if not curr:
        await m.reply_text(
            "ɴᴏ ɢɪᴠᴇᴀᴡᴀʏ ᴛᴏ ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ.\nᴏʀ ᴍᴀʏ ʙᴇ ᴇɴᴛʀɪᴇs ᴀʀᴇ ᴄʟᴏsᴇᴅ ɴᴏᴡ"
        )
        return
    curr = GA.give_info(m.chat.id)
    if not curr["is_give"]:
        await m.reply_text("ɴᴏ ɢɪᴠᴇᴀᴡᴀʏ ᴛᴏ ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ. ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ɴᴇxᴛ ᴏɴᴇ")
        return
    elif not curr["entries"]:
        await m.reply_text(
            "ʏᴏᴜ ᴀʀᴇ ʟᴀᴛᴇ,\nᴇɴᴛʀɪᴇs ᴀʀᴇ ᴄʟᴏsᴇᴅ 🫤\nᴛʀʏ ᴀɢᴀɪɴ ɪɴ ɴᴇxᴛ ɢɪᴠᴇᴀᴡᴀʏ"
        )
        return
    c_id = curr["chat_id"]
    if len(total_entries):
        try:
            if m.from_user.id in total_entries[c_id]:
                await m.reply_text("ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪsᴛᴇʀᴇᴅ.")
                return
        except KeyError:
            pass
    try:
        await c.send_message(m.from_user.id, "ᴛʜᴀɴᴋs ғᴏʀ ᴘᴀʀᴛɪᴄɪᴘᴀᴛɪɴɢ ɪɴ ᴛʜᴇ ɢɪᴠᴇᴀᴡᴀʏ")
    except Exception:
        await m.reply_text(
            "sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ғɪʀsᴛ\nᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ",
            reply_markup=IKM(
                [[IKB("sᴛᴀʀ ᴛʜᴇ ʙᴏᴛ", url=f"https://{Abishnoi.username}.t.me/")]]
            ),
        )
        return
    curr = GA.give_info(m.chat.id)
    c_id = curr["chat_id"]
    if not len(total_entries):
        total_entries[c_id] = [m.from_user.id]
    else:
        try:
            if m.from_user.id not in total_entries[c_id]:
                total_entries[c_id].append(m.from_user.id)
            else:
                pass
        except KeyError:
            total_entries[c_id] = [m.from_user.id]
    await m.reply_text(
        "ʏᴏᴜ ᴀʀᴇ ʀᴇɢɪsᴛᴇʀᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n**ᴅᴏɴ'ᴛ ʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ ᴀʀᴇ ɢᴏɪɴɢ ᴛᴏ ɢᴇᴛ ɪɴғᴏ ᴀʙᴏᴜᴛ ɢɪᴠᴇᴀᴡᴀʏ ᴠɪᴀ ʙᴏᴛ**"
    )
    return


def get_curr_votes(p_id, c_id):
    votess = []
    if votess:
        votess.clear()
    if not len(left_deduct[c_id]):
        votes = 0
        return 0
    for i, j in left_deduct[c_id].items():
        if j == p_id:
            votess.append(i)
    votes = len(votess)
    return votes


@Abishnoi.on_cb("vote_")
async def vote_increment(c: Abishnoi, q: CallbackQuery):
    data = q.data.split("_")
    c_id = int(data[1])
    u_id = int(data[2])
    curr = GA.give_info(c_id)
    if not curr["is_give"]:
        await q.answer("ᴠᴏᴛɪɴɢ ɪs ᴄʟᴏsᴇᴅ")
        return
    if not curr:
        return
    if len(rejoin_try):
        try:
            if q.from_user.id in rejoin_try[c_id]:
                await q.answer(
                    "ʏᴏᴜ ᴄᴀɴ'ᴛ ᴠᴏᴛᴇ. ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ʀᴇ ʀᴇᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ ᴅᴜʀɪɴɢ ɢɪᴠᴇᴀᴡᴀʏ"
                )
                return
        except KeyError:
            pass
    is_old = curr["is_new"]
    can_old = False
    if is_old:
        can_old = datetime.now() - timedelta(days=2)
    try:
        is_part = await c.get_chat_member(c_id, q.from_user.id)
    except UserNotParticipant:
        await q.answer("ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴠᴏᴛᴇ", True)
        return
    if is_part.status not in [CMS.MEMBER, CMS.OWNER, CMS.ADMINISTRATOR]:
        await q.answer("ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴠᴏᴛᴇ", True)
        return
    if can_old and can_old < is_part.joined_date:
        await q.answer("ᴏʟᴅ ᴍᴇᴍʙᴇʀ ᴄᴀɴ'ᴛ ᴠᴏᴛᴇ", True)
        return
    if not len(voted_user):
        voted_user[c_id] = [q.from_user.id]
    elif len(voted_user):
        try:
            if q.from_user.id in voted_user[c_id]:
                await q.answer("ʏᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴠᴏᴛᴇᴅ ᴏɴᴄᴇ", True)
                return
            voted_user[c_id].append(q.from_user.id)
        except KeyError:
            voted_user[c_id] = [q.from_user.id]
    try:
        left_deduct[c_id][q.from_user.id] = u_id
    except KeyError:
        left_deduct[c_id] = {q.from_user.id: u_id}
    votes = get_curr_votes(u_id, c_id)
    try:
        user_entry[c_id][u_id] += 1
        new_vote = IKM([[IKB(f"❤️ {votes}", f"vote_{c_id}_{u_id}")]])
        await q.answer("ᴠᴏᴛᴇᴅ.")
        await q.edit_message_reply_markup(new_vote)
    except KeyError:
        await q.answer("ᴠᴏᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴄʟᴏsᴇᴅ ғᴏʀ ᴛʜɪs ɢɪᴠᴇᴀᴡᴀʏ", True)
        return
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())


@Abishnoi.on_message(filters.left_chat_member)
async def rejoin_try_not(c: Abishnoi, m: Message):
    user = m.left_chat_member
    if not user:
        return
    Ezio = GA.give_info(m.chat.id)
    if not Ezio:
        return
    Captain = user.id
    if len(voted_user):
        if Captain in voted_user[m.chat.id]:
            GB = int(left_deduct[m.chat.id][Captain])
            user_entry[m.chat.id][GB] -= 1
            await c.send_message(
                GB,
                f"ᴏɴᴇ ᴜsᴇʀ ᴡʜᴏ ʜᴀᴠᴇ ᴠᴏᴛᴇᴅ ʏᴏᴜ ʟᴇғᴛ ᴛʜᴇ ᴄʜᴀᴛ sᴏ ʜɪs ᴠᴏᴛᴇ ɪs ʀᴇᴅᴜᴄᴇᴅ ғʀᴏᴍ ʏᴏᴜʀ ᴛᴏᴛᴀʟ ᴠᴏᴛᴇs.\nɴᴏᴛᴇ ᴛʜᴀᴛ ʜᴇ ᴡɪʟʟ ɴᴏᴛ ᴀʙʟᴇ ᴛᴏ ᴠᴏᴛᴇ ɪғ ʜᴇ ʀᴇᴊᴏɪɴs ᴛʜᴇ ᴄʜᴀᴛ\nʟᴇғᴛ ᴜsᴇʀ : {Captain}",
            )
            try:
                rejoin_try[m.chat.id].append(Captain)
            except KeyError:
                rejoin_try[m.chat.id] = [Captain]
    else:
        try:
            rejoin_try[m.chat.id].append(Captain)
        except KeyError:
            rejoin_try[m.chat.id] = [Captain]
        return
