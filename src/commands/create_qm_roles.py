import discord
from src.util.logger import MyLogger
from src.tasks.sync_qm_ranking_roles_task import get_role_name
from src.util.utils import send_message_to_log_channel

logger = MyLogger("CreateQmRoles")


async def create_qm_roles(ctx, bot, ladder):
    """Create QM ranking roles for a specified ladder."""
    if not ctx.message.author.guild_permissions.administrator:
        logger.error(f"{ctx.message.author} is not admin, exiting command.")
        await ctx.send("You must be an administrator to use this command.")
        return

    if not ladder:
        await ctx.send("Usage: `!create_qm_roles <ladder>` (e.g., `!create_qm_roles YR`)")
        return

    ladder = ladder.upper()
    guild = ctx.guild

    # Role ranks to create
    ranks = [1, 3, 5, 10, 25, 50]
    created_roles = []
    existing_roles = []

    try:
        for rank in ranks:
            role_name = get_role_name(ladder, rank)
            if not role_name:
                continue

            # Check if role already exists
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if existing_role:
                existing_roles.append(role_name)
                logger.debug(f"Role '{role_name}' already exists")
            else:
                # Create the role
                await guild.create_role(name=role_name, mentionable=False)
                created_roles.append(role_name)
                logger.log(f"Created role '{role_name}'")

        # Build response message
        response = f"**QM Roles for {ladder}**\n\n"

        if created_roles:
            response += f"✅ Created {len(created_roles)} role(s):\n"
            for role_name in created_roles:
                response += f"  • {role_name}\n"

        if existing_roles:
            response += f"\n⚠️ {len(existing_roles)} role(s) already existed:\n"
            for role_name in existing_roles:
                response += f"  • {role_name}\n"

        if not created_roles and not existing_roles:
            response += "No roles were created."

        await send_message_to_log_channel(bot=bot, msg=response)

    except Exception as e:
        error_msg = f"Error creating roles: {str(e)}"
        logger.exception(error_msg)
        await send_message_to_log_channel(bot=bot, msg=f"❌ {error_msg}")