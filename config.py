import os
from dotenv import load_dotenv
load_dotenv()
# ==== TOKEN & PREFIX ====
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "."
# ==== RUOLI LIVELLI ====
LEVEL_ROLES = {
    5: 1543922260560314407,
    10: 1543922260598071406,
    20: 1543922260598071407,
    50: 1543959134691659826,
    70: 1543959275393523783,
    100: 1543959438480900216,
}
# ==== RUOLO SHOP AURA ====
AURA_SHOP_ROLE = 1543922260598071412
AURA_SHOP_COST = 100000
# ==== RUOLI VERIFICA ====
# Non più hardcoded: si configurano ora per server con i comandi
# "roleverified" (ruolo assegnato alla verifica) e
# "roleunverified" (ruolo rimosso alla verifica), salvati in settings.json
# ==== RUOLI STAFF/TICKET (ping su ogni ticket) ====
# Non più hardcoded: si configurano ora per server (fino a 15 ruoli) con
# il comando "rolestaffconfig" (e si rimuovono con "rolestaffremove"),
# salvati in ticket_config.json
# ==== CANALE RECENSIONI TICKET ====
# Non più hardcoded: si configura ora per server con il comando
# "rateconfig" (e si rimuove con "rateremove"), salvato in ticket_config.json
# ==== CANALI DA CONFIGURARE (metti gli ID reali) ====
WELCOME_CHANNEL_ID = None
GOODBYE_CHANNEL_ID = None
WELCOME_GOODBYE_LOG_CHANNEL_ID = None
INVITES_LOG_CHANNEL_ID = None
AUTOMOD_LOG_CHANNEL_ID = None
TICKET_CATEGORY_ID = None  # categoria dove creare i canali ticket
# ==== ECONOMIA ====
CURRENCY_NAME = "Aura Coins"
BOX_PRICES = {
    "comuni": 150,
    "rare": 300,
    "epiche": 500,
    "mitiche": 750,
    "leggendaria": 1000,
}
