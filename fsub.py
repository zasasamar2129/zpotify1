from pyrogram.errors import UserNotParticipant, PeerIdInvalid, UserIsBlocked, ChatWriteForbidden
from pyrogram import enums, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mbot import Mbot, LOG_GROUP as BUG,F_SUB,F_SUB_CHANNEL_ID, F_SUB_CHANNEL_INVITE_LINK, paste
from requests import post 
import traceback 

async def Fsub(message, Mbot, user_id):
      try:
          if user_id  == 5268375124:
             return 
          try:
              get_member = await Mbot.get_chat_member(chat_id=F_SUB_CHANNEL_ID,user_id=user_id)
          except UserNotParticipant:
              await message.reply(
    "Sᴏʀʀʏ Sɪʀ/ Mᴀᴅᴀᴍ 🥲\n\n"
    "    Iɴ ᴏʀᴅᴇʀ ᴛᴏ ᴜsᴇ ᴍᴇ, ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ\n\n"
    "Nᴏᴛᴇ:\n"
    "    Iғ ʏᴏᴜ ᴇɴᴄᴏᴜɴᴛᴇʀ ᴀɴʏ ɪssᴜᴇs, ʏᴏᴜ ᴄᴀɴ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ sᴋɪᴘ ᴊᴏɪɴɪɴɢ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.\n\n"
    "Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ!\n"
    "Jᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴘʀᴇss ᴛʜᴇ ʀᴇғʀᴇsʜ ʙᴜᴛᴛᴏɴ.",
    reply_markup=InlineKeyboardMarkup([
         [InlineKeyboardButton("Join Channel 📣", url=F_SUB_CHANNEL_INVITE_LINK)],
        [InlineKeyboardButton("Refresh 🔄", callback_data="refresh")]
    ])
              )
              raise StopPropagation
          except PeerIdInvalid:
              try:
                  await Mbot.send_chat_action(chat_id=user_id,action=enums.ChatAction.TYPING)
                  get_member = await Mbot.get_chat_member(chat_id=F_SUB_CHANNEL_ID,user_id=user_id)
              except PeerIdInvalid:
                  pass
              except UserIsBlocked:
                  pass
              except UserNotParticipant:
                  await message.reply(
    "Sᴏʀʀʏ Sɪʀ/ Mᴀᴅᴀᴍ 🥲\n\n"
    "    Iɴ ᴏʀᴅᴇʀ ᴛᴏ ᴜsᴇ ᴍᴇ, ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ\n\n"
    "Nᴏᴛᴇ:\n"
    "    Iғ ʏᴏᴜ ᴇɴᴄᴏᴜɴᴛᴇʀ ᴀɴʏ ɪssᴜᴇs, ʏᴏᴜ ᴄᴀɴ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ sᴋɪᴘ ᴊᴏɪɴɪɴɢ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.\n\n"
    "Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ!\n"
    "Jᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴘʀᴇss ᴛʜᴇ ʀᴇғʀᴇsʜ ʙᴜᴛᴛᴏɴ.",
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Channel 📣", url=F_SUB_CHANNEL_INVITE_LINK)],
        [InlineKeyboardButton("Refresh 🔄", callback_data="refresh")]
    ])
                  )
                  raise StopPropagation
      except (StopPropagation, ChatWriteForbidden):
          raise StopPropagation
      except Exception as e:
          await Mbot.send_message(BUG, f"#Fsub module Exception Raised {e}\n {paste(traceback.format_exc())}")
          await message.reply('503: Sorry, We Are Unable To Procced It 🤕❣️')     
      for var in list(locals()):
        if var != '__name__' and var != '__doc__':
            del locals()[var]
