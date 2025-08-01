import os
import discord
from discord.ext import commands
import asyncio
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager
from dotenv import load_dotenv  # Thêm dòng này để hỗ trợ .env

class DiscordBot(commands.Bot):
    """
    Discord bot cho trading: slash command, push notify, nhận lệnh tay, báo cáo trạng thái, SafeMode...
    """
    def __init__(self, capital_manager, risk_controller, execution_engine, config_dir="config"):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.config = ConfigLoader(config_dir)
        self.logger = LogManager.get_logger("discord")
        self.capital_manager = capital_manager
        self.risk_controller = risk_controller
        self.execution_engine = execution_engine

        # Load .env và lấy channel_id từ biến môi trường
        load_dotenv()
        self.channel_id = int(os.getenv("DISCORD_CHANNEL_ID", 0))
        self.add_commands()

    def add_commands(self):
        @self.command(name="status")
        async def status(ctx):
            """Báo cáo trạng thái vốn, risk, lệnh open"""
            report = self.capital_manager.report()
            risk = self.risk_controller.report()
            msg = f"**Capital Report:**\nBalance: {report['balance']}\nDaily PnL: {report['daily_pnl']}\nOpen Positions: {len(report['open_positions'])}\n\n"
            msg += f"**Risk:**\nSafeMode: {risk['safe_mode']}\nDrawdown: {risk['drawdown']}\nLoss Streak: {risk['loss_streak']}\n"
            await ctx.send(msg)

        @self.command(name="safemode")
        async def safemode(ctx, arg="on"):
            """Bật/tắt SafeMode thủ công"""
            if arg.lower() == "on":
                self.risk_controller.trigger_safe_mode("manual")
                await ctx.send("SafeMode đã bật. Dừng giao dịch.")
            else:
                self.risk_controller.safe_mode = False
                await ctx.send("SafeMode đã tắt. Bot sẽ giao dịch lại.")

        @self.command(name="order")
        async def order(ctx, symbol: str, side: str, size: float, price: float = None):
            """Đặt lệnh tay: !order BTCUSDT buy 100 30000"""
            proposal = {"symbol": symbol, "side": side, "size": size, "entry_price": price}
            order = self.execution_engine.place_order(proposal)
            if order:
                await ctx.send(f"Đã đặt lệnh {side} {symbol} size {size} giá {price or 'market'}")
            else:
                await ctx.send("Đặt lệnh thất bại hoặc đang SafeMode.")

        @self.command(name="closeall")
        async def closeall(ctx):
            """Đóng toàn bộ lệnh đang mở"""
            count = 0
            for order in list(self.execution_engine.open_orders):
                self.execution_engine.close_order(order["id"], order.get("tp", order["entry_price"]))
                count += 1
            await ctx.send(f"Đã đóng {count} lệnh.")

        @self.command(name="help")
        async def help_cmd(ctx):
            msg = (
                "**Lệnh Discord bot:**\n"
                "`!status` - Xem trạng thái vốn/risk\n"
                "`!safemode on/off` - Bật/tắt SafeMode thủ công\n"
                "`!order SYMBOL SIDE SIZE [PRICE]` - Đặt lệnh tay (ví dụ: !order BTCUSDT buy 100 30000)\n"
                "`!closeall` - Đóng toàn bộ lệnh\n"
            )
            await ctx.send(msg)

    async def notify(self, msg):
        """Gửi notify tới kênh Discord định sẵn (dùng cho trade, alert, PnL, SafeMode...)"""
        await self.wait_until_ready()
        try:
            channel = self.get_channel(self.channel_id)
            if channel:
                await channel.send(msg)
            else:
                self.logger.error(f"Discord channel {self.channel_id} not found.")
        except Exception as e:
            self.logger.error(f"Discord notify error: {e}")

# Usage example: Chạy bot thực tế
if __name__ == "__main__":
    from capital.capital_manager import CapitalManager
    from risk.risk_controller import RiskController
    from execution.execution_engine import ExecutionEngine

    # Dummy instance for demo (thay bằng real client/engine)
    class DummyClient:
        def create_order(self, **kwargs): return {**kwargs, "id": 123}
        def update_stop_loss(self, order_id, sl): pass

    load_dotenv()  # Đảm bảo load .env cho đoạn main này

    cm = CapitalManager()
    rc = RiskController()
    ee = ExecutionEngine(DummyClient(), cm, rc)

    # Lấy token từ .env thay vì từ config
    bot_token = os.getenv("DISCORD_TOKEN")
    bot = DiscordBot(cm, rc, ee)
    print("Discord bot running... Use !status, !order, !safemode, !closeall")
    bot.run(bot_token)
