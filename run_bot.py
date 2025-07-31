from pipeline.data_pipeline import DataPipeline
from capital.capital_manager import CapitalManager
from ai.ai_engine import AIEngine
from strategy.strategy_engine import StrategyEngine
from risk.risk_controller import RiskController
from execution.execution_engine import ExecutionEngine
from discord.discord_bot import DiscordBot
from webhook.webhook_server import WebhookQueue, WebhookServer
from safemode.safemode_system import SafeModeSystem

def on_new_candle(symbol, timeframe, candles):
    ai_signal = ai_engine.ensemble_predict(symbol, extract_features(candles), extract_series(candles), extract_state(candles))
    proposal = strategy_engine.propose_trade(ai_signal, candles)
    if proposal:
        # Thêm size, price nếu cần
        proposal["size"] = capital_manager.get_position_size({"winrate": 0.6, "rr": 2.0})
        proposal["entry_price"] = candles[-1]["close"]
        execution_engine.place_order(proposal)

if __name__ == "__main__":
    data_pipeline = DataPipeline()
    capital_manager = CapitalManager()
    ai_engine = AIEngine()
    strategy_engine = StrategyEngine()
    risk_controller = RiskController()
    # Dummy client cần thay bằng API thực tế
    class DummyClient: ...
    client = DummyClient()
    execution_engine = ExecutionEngine(client, capital_manager, risk_controller)
    discord_bot = DiscordBot(capital_manager, risk_controller, execution_engine)
    safemode_system = SafeModeSystem(risk_controller, discord_bot)
    queue = WebhookQueue()
    webhook_server = WebhookServer(queue)
    webhook_server.start()

    # Kết nối pipeline
    data_pipeline.trigger_on_new_candle = on_new_candle

    # Có thể chạy các worker khác bằng thread nếu cần (Dashboard, SafeMode monitor...)

    print("Bot is running...")

    # Giả lập nến mới
    # while True:
    #     data_pipeline.append_candle("BTCUSDT", "15m", get_new_candle())
    #     time.sleep(60)
