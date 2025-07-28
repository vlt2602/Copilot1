import discord
from discord.ext import commands

class DiscordBot(commands.Bot):
    def __init__(self, pipeline):
        super().__init__(command_prefix="/")
        self.pipeline = pipeline

    async def on_ready(self):
        print(f"Bot online as {self.user}")

    @commands.command()
    async def start(self, ctx):
        await ctx.send("Pipeline started!")
        self.pipeline.run()

    @commands.command()
    async def stop(self, ctx):
        await ctx.send("Pipeline stopped!")
        # TODO: Stop logic

    # Thêm các lệnh khác tương tự
