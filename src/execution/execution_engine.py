import time
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager

class ExecutionEngine:
    """
    Đặt lệnh, quản lý trạng thái, trailing SL/TP, retry, batch.
    Tích hợp với CapitalManager, RiskController, log mọi hoạt động order.
    """
    def __init__(self, client, capital_manager, risk_controller, config_dir="config"):
        self.client = client  # Instance sàn (Binance, Bybit API wrapper)
        self.capital_manager = capital_manager
        self.risk_controller = risk_controller
        self.config = ConfigLoader(config_dir)
        self.logger = LogManager.get_logger("order")
        self.open_orders = []

    def place_order(self, proposal):
        """
        Đặt lệnh mua/bán theo đề xuất từ Strategy, đã kiểm soát risk/capital.
        """
        if not self.risk_controller.should_trade():
            self.logger.warning("Trading in SafeMode, order skipped.")
            return None

        size = proposal.get("size")
        symbol = proposal["symbol"]
        side = proposal["side"]
        sl = proposal.get("sl")
        tp = proposal.get("tp")
        trailing = proposal.get("trailing", {})
        price = proposal.get("entry_price")

        # Check max position size
        if not self.risk_controller.check_max_position(size, self.capital_manager.balance):
            self.logger.warning(f"Order skipped: size {size} > max allowed.")
            return None

        try:
            # Thực tế: gọi API client để đặt lệnh
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                size=size,
                price=price,  # hoặc market nếu None
                sl=sl,
                tp=tp
            )
            self.open_orders.append(order)
            self.logger.info(f"ORDER PLACED: {order}")
            # Ghi nhận position cho CapitalManager
            self.capital_manager.add_position(symbol, size, price, side)
            return order
        except Exception as e:
            self.logger.error(f"ORDER FAILED: {symbol} {side} {size}: {e}")
            # Retry logic: thử lại 1 lần nếu lỗi mạng
            time.sleep(1)
            try:
                order = self.client.create_order(
                    symbol=symbol, side=side, size=size, price=price, sl=sl, tp=tp
                )
                self.open_orders.append(order)
                self.capital_manager.add_position(symbol, size, price, side)
                self.logger.info(f"ORDER RETRY SUCCESS: {order}")
                return order
            except Exception as e2:
                self.logger.error(f"ORDER RETRY FAILED: {e2}")
                self.risk_controller.on_trade_result(-size * 0.01)  # Giả lập loss nhẹ do fail
                return None

    def update_trailing(self, order, market_price):
        """
        Quản lý trailing SL/TP động cho 1 order.
        """
        trailing = order.get("trailing", {})
        if not trailing.get("enabled", False):
            return
        trigger_pct = trailing.get("trigger_pct", 1.5)
        trail_pct = trailing.get("trail_pct", 0.4)
        entry = order["entry_price"]
        side = order["side"]
        sl = order.get("sl")
        # Nếu market vượt trigger, cập nhật SL mới
        if side == "buy" and market_price >= entry * (1 + trigger_pct / 100):
            new_sl = market_price * (1 - trail_pct / 100)
            if not sl or new_sl > sl:
                self.client.update_stop_loss(order["id"], new_sl)
                order["sl"] = new_sl
                self.logger.info(f"Trailing SL updated for {order['symbol']}: {new_sl}")
        if side == "sell" and market_price <= entry * (1 - trigger_pct / 100):
            new_sl = market_price * (1 + trail_pct / 100)
            if not sl or new_sl < sl:
                self.client.update_stop_loss(order["id"], new_sl)
                order["sl"] = new_sl
                self.logger.info(f"Trailing SL updated for {order['symbol']}: {new_sl}")

    def close_order(self, order_id, exit_price):
        """
        Chốt lệnh, cập nhật PnL, trạng thái.
        """
        for idx, order in enumerate(self.open_orders):
            if order["id"] == order_id:
                pnl = self.capital_manager.close_position(idx, exit_price)
                self.logger.info(f"ORDER CLOSED: {order_id}, PnL: {pnl:.2f}")
                # Thông báo RiskController
                self.risk_controller.on_trade_result(pnl)
                del self.open_orders[idx]
                return pnl
        self.logger.warning(f"Order {order_id} not found for closing.")
        return None

    def batch_orders(self, proposals):
        """
        Đặt nhiều lệnh cùng lúc (batch processing).
        """
        results = []
        for proposal in proposals:
            res = self.place_order(proposal)
            results.append(res)
        return results

    def monitor_orders(self, market_data):
        """
        Theo dõi trạng thái lệnh, update trailing SL/TP nếu cần.
        """
        for order in list(self.open_orders):
            symbol = order["symbol"]
            price = market_data.get(symbol)
            if price:
                self.update_trailing(order, price)

# Usage example/test
if __name__ == "__main__":
    class DummyClient:
        def create_order(self, **kwargs):
            return {**kwargs, "id": int(time.time())}
        def update_stop_loss(self, order_id, sl):
            print(f"Dummy SL update for order {order_id}: {sl}")

    from capital.capital_manager import CapitalManager
    from risk.risk_controller import RiskController

    client = DummyClient()
    cm = CapitalManager()
    rc = RiskController()
    ee = ExecutionEngine(client, cm, rc)
    proposal = {"symbol": "BTCUSDT", "side": "buy", "size": 100, "entry_price": 30000, "sl": 29500, "tp": 31000, "trailing": {"enabled": True, "trigger_pct": 1.5, "trail_pct": 0.4}}
    order = ee.place_order(proposal)
    ee.update_trailing(order, 30500)
    pnl = ee.close_order(order["id"], 31000)
    print("Closed PnL:", pnl)
