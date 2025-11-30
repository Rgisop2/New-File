from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper.verification import VerificationManager
from helper.helper_func import decode, get_messages, force_sub
from plugins.shortner import get_short
from config import LOGGER, OWNER_ID
from datetime import datetime, timedelta
import asyncio

verification_manager = VerificationManager()

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_with_verification(client: Client, message: Message):
    """Handle /start with verification system"""
    user_id = message.from_user.id
    text = message.text

    if len(text) <= 7:
        # Normal start command - let other handlers handle it
        return
    
    try:
        payload = text.split(" ", 1)[1]
        
        # ========== VERIFICATION TOKEN HANDLER ==========
        if payload.startswith("verify_"):
            await handle_verification_token(client, message, user_id, payload)
            return
        
        # ========== FILE ACCESS HANDLER ==========
        # Check if this is a shortner wrapped link or normal link
        is_short_link = payload.startswith("yu3elk")
        if is_short_link:
            base64_payload = payload[6:-1]
        else:
            base64_payload = payload
        
        # Use file_id as unique identifier for this access attempt
        file_id = base64_payload
        
        # Check verification status
        status = await verification_manager.check_verification_status(
            file_id, user_id, client.mongodb, gap_time_minutes=5
        )
        
        # ========== STEP 0: FIRST VERIFICATION NEEDED ==========
        if status["current_step"] == 0:
            token_1 = await verification_manager.start_first_verification(file_id, user_id, client.mongodb)
            
            verify_link = f"https://t.me/{client.username}?start=verify_{token_1}"
            
            short_link = await get_short_link(client, verify_link, verification_step=1)
            
            if not short_link:
                await message.reply(
                    "❌ <b>Shortener Failed</b>\n\n"
                    "Unable to generate verification link. Please try again later."
                )
                return
            
            await message.reply(
                "<b>🔒 Verification Required (Step 1/2)</b>\n\n"
                "Your verification code will be sent to you after clicking the button below.\n\n"
                "<blockquote>This helps us protect your files.</blockquote>"
            )
            
            await message.reply(
                "Click the button below to verify:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✓ Verify Now", url=short_link)]
                ])
            )
            return
        
        # ========== STEP 1: CHECK IF GAP TIME EXPIRED ==========
        elif status["gap_expired"]:
            token_2 = await verification_manager.start_second_verification(file_id, user_id, client.mongodb)
            
            verify_link = f"https://t.me/{client.username}?start=verify_{token_2}"
            
            short_link = await get_short_link(client, verify_link, verification_step=2)
            
            if not short_link:
                await message.reply(
                    "❌ <b>Shortener Failed</b>\n\n"
                    "Unable to generate verification link. Please try again later."
                )
                return
            
            await message.reply(
                "<b>🔒 Second Verification Required (Step 2/2)</b>\n\n"
                "Your temporary access has expired. Please verify once more.\n\n"
                "<blockquote>This is your final verification for this session.</blockquote>"
            )
            
            await message.reply(
                "Click the button below to verify:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✓ Verify Now", url=short_link)]
                ])
            )
            return
        
        # ========== VERIFIED: SEND FILE ==========
        elif status["can_access_file"]:
            # User is verified and accessing via normal file link, send file
            await send_file_with_verification(client, message, base64_payload, is_short_link, file_id, user_id)
            return
    
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Verification start error: {e}")


async def get_short_link(client: Client, url: str, verification_step: int = 1) -> str:
    """
    Helper to get shortened link with error handling
    Returns shortened URL or None if failed
    """
    try:
        from plugins.shortner import get_short
        short_link = get_short(url, client, verification_step=verification_step)
        return short_link
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Error shortening link: {e}")
        return None


async def handle_verification_token(client: Client, message: Message, user_id: int, payload: str):
    """
    Handle verification token submission - only accept valid unused tokens
    """
    try:
        # Extract token from payload
        token = payload.split("_", 1)[1] if "_" in payload else None
        
        if not token:
            await message.reply("⚠️ Invalid verification token.")
            return
        
        ver_record = None
        async for doc in client.mongodb.user_data.find({
            "$or": [
                {"token_1": token, "token_1_used": False},
                {"token_2": token, "token_2_used": False}
            ]
        }):
            ver_record = doc
            break
        
        if not ver_record:
            await message.reply("⚠️ Verification token not found, expired, or already used.")
            return
        
        file_id = ver_record.get("file_id")
        current_step = ver_record.get("current_step", 0)
        
        # ========== VERIFY TOKEN 1 ==========
        if current_step == 0 and ver_record.get("token_1") == token and not ver_record.get("token_1_used"):
            result = await verification_manager.verify_token_1(
                file_id, user_id, token, gap_time_minutes=5, mongodb=client.mongodb
            )
            
            if result["success"]:
                gap_end_str = result["gap_end"].strftime("%H:%M:%S")
                await message.reply(
                    f"✅ <b>First Verification Successful!</b>\n\n"
                    f"<blockquote>You have <b>5 minutes</b> to access your files without re-verification.</blockquote>\n\n"
                    f"<code>Session expires at: {gap_end_str}</code>\n\n"
                    f"<a href='https://t.me/{client.username}?start={file_id}'>Click here to get your files</a>"
                )
            else:
                await message.reply(f"❌ First verification failed: {result['message']}")
        
        # ========== VERIFY TOKEN 2 ==========
        elif current_step == 1 and ver_record.get("token_2") == token and not ver_record.get("token_2_used"):
            result = await verification_manager.verify_token_2(file_id, user_id, token, mongodb=client.mongodb)
            
            if result["success"]:
                await message.reply(
                    f"✅ <b>Second Verification Successful!</b>\n\n"
                    f"<blockquote>You are now fully verified!</blockquote>\n\n"
                    f"You can now access files without further verification.\n\n"
                    f"<a href='https://t.me/{client.username}?start={file_id}'>Click here to get your files</a>"
                )
            else:
                await message.reply(f"❌ Second verification failed: {result['message']}")
        
        else:
            await message.reply("⚠️ Token verification not possible at this stage or token has been used.")
    
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Verification token handler error: {e}")
        await message.reply("⚠️ An error occurred during verification.")


async def send_file_with_verification(client: Client, message: Message, base64_payload: str, is_short_link: bool, file_id: str, user_id: int):
    """Send files to verified user"""
    try:
        # Decode base64 to get file IDs
        from helper.helper_func import encode
        string = await decode(base64_payload)
        argument = string.split("-")
        ids = []
        source_channel_id = None

        if len(argument) == 3:
            encoded_start = int(argument[1])
            encoded_end = int(argument[2])
            
            primary_multiplier = abs(client.db)
            start_primary = int(encoded_start / primary_multiplier)
            end_primary = int(encoded_end / primary_multiplier)
            
            if encoded_start % primary_multiplier == 0 and encoded_end % primary_multiplier == 0:
                source_channel_id = client.db
                start = start_primary
                end = end_primary
            else:
                db_channels = getattr(client, 'db_channels', {})
                for channel_id_str in db_channels.keys():
                    channel_id = int(channel_id_str)
                    channel_multiplier = abs(channel_id)
                    start_test = int(encoded_start / channel_multiplier)
                    end_test = int(encoded_end / channel_multiplier)
                    
                    if encoded_start % channel_multiplier == 0 and encoded_end % channel_multiplier == 0:
                        source_channel_id = channel_id
                        start = start_test
                        end = end_test
                        break
                
                if source_channel_id is None:
                    source_channel_id = client.db
                    start = start_primary
                    end = end_primary
            
            ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

        elif len(argument) == 2:
            encoded_msg = int(argument[1])
            
            if hasattr(client, 'db_channel') and client.db_channel:
                primary_multiplier = abs(client.db_channel.id)
                msg_id_primary = int(encoded_msg / primary_multiplier)
                
                if encoded_msg % primary_multiplier == 0:
                    source_channel_id = client.db_channel.id
                    ids = [msg_id_primary]
                else:
                    db_channels = getattr(client, 'db_channels', {})
                    for channel_id_str in db_channels.keys():
                        channel_id = int(channel_id_str)
                        channel_multiplier = abs(channel_id)
                        msg_id_test = int(encoded_msg / channel_multiplier)
                        
                        if encoded_msg % channel_multiplier == 0:
                            source_channel_id = channel_id
                            ids = [msg_id_test]
                            break
                    
                    if source_channel_id is None:
                        source_channel_id = client.db_channel.id if hasattr(client, 'db_channel') else client.db
                        ids = [msg_id_primary]
            else:
                source_channel_id = client.db
                ids = [int(encoded_msg / abs(client.db))]

        temp_msg = await message.reply("Wait A Sec..")
        messages = []

        try:
            if source_channel_id:
                try:
                    msgs = await client.get_messages(chat_id=source_channel_id, message_ids=list(ids))
                    valid_msgs = [msg for msg in msgs if msg is not None]
                    messages.extend(valid_msgs)
                    
                    if len(valid_msgs) < len(list(ids)):
                        missing_ids = [mid for mid in ids if mid not in {msg.id for msg in valid_msgs}]
                        if missing_ids:
                            additional_messages = await get_messages(client, missing_ids)
                            messages.extend(additional_messages)
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"Error getting messages: {e}")
                    messages = await get_messages(client, ids)
            else:
                messages = await get_messages(client, ids)
        except Exception as e:
            await temp_msg.edit_text("Something went wrong!")
            client.LOGGER(__name__, client.name).warning(f"Error fetching messages: {e}")
            return

        if not messages:
            return await temp_msg.edit("Couldn't find the files in the database.")
        
        await temp_msg.delete()

        # Send all files
        for msg in messages:
            caption = msg.caption.html if msg.caption else (msg.document.file_name if msg.document else "")
            reply_markup = msg.reply_markup if not client.disable_btn else None

            try:
                await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    protect_content=client.protect
                )
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to send message: {e}")

    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Send file error: {e}")
        await message.reply("⚠️ An error occurred while sending files.")
