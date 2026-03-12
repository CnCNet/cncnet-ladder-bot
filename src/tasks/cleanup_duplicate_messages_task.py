"""
Periodic cleanup task to remove duplicate messages from bot channels.

This task runs periodically to ensure only one message exists in each bot channel.
If multiple messages are found, it keeps the most recent one and deletes the rest.
"""
from discord.ext.commands import Bot
from src.commands.get_active_matches import last_summary_message_ids
from src.constants.constants import DEV_DISCORD_ID, DISCORDS, QM_BOT_CHANNEL_NAME
from src.util.logger import MyLogger
from src.util.utils import send_message_to_log_channel

logger = MyLogger("cleanup_duplicate_messages_task")


async def execute(bot: Bot, debug: bool) -> None:
    """
    Clean up duplicate messages in bot channels.

    For each configured bot channel:
    1. Fetch all messages
    2. If more than 1 message exists, keep the most recent and delete the rest
    3. Update the message cache with the kept message's ID

    Args:
        bot: Discord bot instance
        debug: Whether running in debug mode (only processes dev server if True)
    """
    logger.debug("Starting cleanup_duplicate_messages_task()...")

    for server in bot.guilds:
        # Skip based on debug mode
        if (server.id == DEV_DISCORD_ID) != debug:
            continue

        server_info = DISCORDS.get(server.id)
        if server_info is None:
            logger.warning(f"Unexpected server ID: {server.id} (server name: {server.name}) ... skipping")
            continue

        qm_bot_channel = bot.get_channel(server_info["qm_bot_channel_id"])

        if not qm_bot_channel:
            logger.error(f"Channel not found for {server.name}: {server_info['qm_bot_channel_id']}")
            continue

        try:
            # Fetch all messages in the channel (limit to 100 for safety)
            messages = []
            async for message in qm_bot_channel.history(limit=100):
                # Only consider bot's own messages
                if message.author.id == bot.user.id:
                    messages.append(message)

            message_count = len(messages)

            if message_count == 0:
                logger.debug(f"No messages in '{server.name}.{qm_bot_channel.name}', skipping cleanup")
                continue
            elif message_count == 1:
                # Update cache with the single message ID
                channel_id = qm_bot_channel.id
                if channel_id not in last_summary_message_ids or last_summary_message_ids[channel_id] != messages[0].id:
                    last_summary_message_ids[channel_id] = messages[0].id
                    logger.debug(f"Updated cache for '{server.name}.{qm_bot_channel.name}' with message ID {messages[0].id}")
            else:
                # Multiple messages found - keep the most recent, delete the rest
                logger.warning(
                    f"Found {message_count} messages in '{server.name}.{qm_bot_channel.name}', "
                    f"cleaning up duplicates..."
                )

                # Sort by timestamp (most recent first)
                messages.sort(key=lambda m: m.created_at, reverse=True)

                # Keep the first (most recent) message
                keep_message = messages[0]
                delete_messages = messages[1:]

                # Delete old messages
                deleted_count = 0
                for message in delete_messages:
                    try:
                        await message.delete()
                        deleted_count += 1
                        logger.debug(f"Deleted message {message.id} from '{server.name}.{qm_bot_channel.name}'")
                    except Exception as e:
                        logger.error(f"Failed to delete message {message.id}: {e}")

                # Update cache with the kept message
                channel_id = qm_bot_channel.id
                last_summary_message_ids[channel_id] = keep_message.id

                success_msg = (
                    f"Cleaned up {deleted_count} duplicate message(s) in "
                    f"'{server.name}.{qm_bot_channel.name}', kept message {keep_message.id}"
                )
                logger.log(success_msg)
                await send_message_to_log_channel(bot=bot, msg=success_msg)

        except Exception as e:
            error_msg = (
                f"Error during cleanup in '{server.name}.{qm_bot_channel.name}': "
                f"{type(e).__name__}: {e}"
            )
            logger.error(error_msg)
            await send_message_to_log_channel(bot=bot, msg=error_msg)

    logger.debug("Completed cleanup_duplicate_messages_task()")
