BURG_ID = 123726717067067393  # Burg discord profile ID

# Discord server IDs
YR_DISCORD_ID = 252268956033875970  # Yuri's Revenge - Server ID
CNCNET_DISCORD_ID = 188156159620939776
BLITZ_DISCORD_ID = 818265922615377971
DEV_DISCORD_ID = 1089195585984286860

# discords where this bot resides
DISCORDS = {
    BLITZ_DISCORD_ID:
        {
            "qm_bot_channel_id": 1040396984164548729,  # channel where messages are sent
            "ladders": ["blitz", "blitz-2v2", "ra2", "yr", "ra2-2v2"]  # list of which ladders data will be retrieved
        },
    YR_DISCORD_ID:
        {
            "qm_bot_channel_id": 1039026321826787338,
            "ladders": ["ra2", "yr", "blitz", "blitz-2v2", "ra2-2v2"]
        },
    CNCNET_DISCORD_ID:
        {
            "qm_bot_channel_id": 1039608594057924609,
            "ladders": ["d2k", "ra", "ra-2v2", "ra2", "ra2-2v2", "yr", "blitz", "blitz-2v2"]
        },
    DEV_DISCORD_ID: {
        "qm_bot_channel_id": 1373149510372560987,
        "ladders": ["ra2", "yr", "blitz-2v2"]
    }
}

QM_BOT_CHANNEL_NAME = "ladder-bot"

CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID = 1240364999931854999  # cncnet ladder development discord, #bot-logs channel ID
