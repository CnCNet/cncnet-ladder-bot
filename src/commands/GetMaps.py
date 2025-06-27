from src.util.MyLogger import MyLogger
from src.util.Utils import send_message_to_log_channel, is_error, get_exception_msg

logger = MyLogger("GetMaps")


async def get_maps(ctx, bot, arg, ladders, cnc_api_client):
    logger.debug(f"Fetching maps for ladder '{arg}'")

    if not ladders:
        await ctx.send("Error: No ladders available")
        return

    if not arg:
        ladders_string = ', '.join(ladders)
        await ctx.send(f"No ladder provided, select a valid ladder from `[{ladders_string}]`, like `!maps ra2`")
        return

    if arg.lower() not in ladders:
        ladders_string = ', '.join(ladders)
        await ctx.send(f"{arg.lower()} is not a valid ladder from `{ladders_string}`")
        return

    maps_json = cnc_api_client.fetch_maps(arg.lower())

    if is_error(maps_json):
        await ctx.send(f"Error fetching maps for ladder {arg.lower()}")
        await send_message_to_log_channel(bot=bot, msg=get_exception_msg(e=maps_json))
        return

    maps_arr = [f"({item['map_tier']}) {item['description']}"
                for item in maps_json if 'map_tier' in item and 'description' in item]

    if not maps_arr:
        await ctx.send(f"Error: No maps found in ladder': {arg.upper()}'")
        return

    maps_string = "\n" + "\n".join(maps_arr)
    message = f"{len(maps_arr)} **{arg.upper()}** maps:\n```{maps_string}\n```"

    await ctx.send(message[:2000])
