from src.pipeline.pipeline import run_pipeline
from src.bot.discord_bot import DiscordBot
from src.bot.webhook_server import WebhookServer

def run_bot():
    print("THopper Bot Starting...")
    # Khởi động pipeline
    run_pipeline()
    # Khởi động Discord bot
    discord_bot = DiscordBot()
    discord_bot.start()
    # Khởi động webhook server
    webhook_server = WebhookServer()
    webhook_server.start()
