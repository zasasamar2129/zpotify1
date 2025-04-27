from pyrogram.errors import UserNotParticipant, PeerIdInvalid, UserIsBlocked, ChatWriteForbidden
from pyrogram import enums, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mbot import Mbot, LOG_GROUP as BUG, F_SUB, F_SUB_CHANNEL_IDS, F_SUB_CHANNEL_INVITE_LINKS, paste
from requests import post 
import traceback 

from pyrogram import utils

def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"

utils.get_peer_type = get_peer_type_new

async def Fsub(message, Mbot, user_id):
    try:
        if user_id == 5268375124:
            return
        
        unjoined_channels = []
        keyboard = []
        
        # Check membership and get channel info
        for idx, (channel_id, invite_link) in enumerate(zip(F_SUB_CHANNEL_IDS, F_SUB_CHANNEL_INVITE_LINKS)):
            try:
                # Get channel info
                chat = await Mbot.get_chat(int(channel_id))
                channel_name = chat.title
            except Exception as e:
                channel_name = f"Channel {idx+1}"  # Fallback name
                
            try:
                await Mbot.get_chat_member(chat_id=int(channel_id), user_id=user_id)
            except UserNotParticipant:
                unjoined_channels.append((channel_name, invite_link))
            except Exception as e:
                await Mbot.send_message(BUG, f"Fsub Error: {e}\n{traceback.format_exc()}")

        # If user hasn't joined some channels
        if unjoined_channels:
            buttons = []
            text_lines = [
                "Sᴏʀʀʏ Sɪʀ/ Mᴀᴅᴀᴍ 🥲\n\n",
                "Iɴ ᴏʀᴅᴇʀ ᴛᴏ ᴜsᴇ ᴍᴇ, ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs:\n\n"
            ]
            
            for channel_name, invite_link in unjoined_channels:
                buttons.append([InlineKeyboardButton(f"Join {channel_name} 📣", url=invite_link)])
                text_lines.append(f"➤ {channel_name}\n")
            
            text_lines.extend([
                "\nNᴏᴛᴇ:\n",
                "Aғᴛᴇʀ ᴊᴏɪɴɪɴɢ ᴀʟʟ ᴄʜᴀɴɴᴇʟs, ᴄʟɪᴄᴋ ᴛʜᴇ ʀᴇғʀᴇsʜ ʙᴜᴛᴛᴏɴ.\n",
                "Iғ ʏᴏᴜ ᴇɴᴄᴏᴜɴᴛᴇʀ ɪssᴜᴇs, ʏᴏᴜ ᴄᴀɴ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ sᴋɪᴘ ᴛʜɪs sᴛᴇᴘ."
            ])
            
            buttons.append([InlineKeyboardButton("Refresh 🔄", callback_data="refresh")])
            
            await message.reply(
                "".join(text_lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
            raise StopPropagation

    except (StopPropagation, ChatWriteForbidden):
        raise StopPropagation
    except Exception as e:
        await Mbot.send_message(BUG, f"#Fsub module Exception: {e}\n{paste(traceback.format_exc())}")
        await message.reply('503: Sorry, We Are Unable To Process Your Request 🤕❣️')

        for var in list(locals()):
            if var != '__name__' and var != '__doc__':
                del locals()[var]
