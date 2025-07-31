import streamlit as st
import time
import threading

class DashboardApp:
    """
    Dashboard realtime: hiển thị vốn, PnL, trạng thái SafeMode, log, lệnh mở...
    Có thể tích hợp thêm trạng thái AI, Risk, Execution.
    """
    def __init__(self, capital_manager, risk_controller, execution_engine, ai_engine=None):
        self.capital_manager = capital_manager
        self.risk_controller = risk_controller
        self.execution_engine = execution_engine
        self.ai_engine = ai_engine

    def run(self, refresh_sec=5):
        st.set_page_config(page_title="THopper PRO++ Dashboard", layout="wide")
        st.title("THopper PRO++ Dashboard")
        last_update = st.empty()

        while True:
            st.empty()  # clear for rerun
            col1, col2, col3 = st.columns(3)

            # Capital info
            with col1:
                st.header("💰 Capital")
                report = self.capital_manager.report()
                st.metric("Balance", report["balance"])
                st.metric("Daily PnL", report["daily_pnl"])
                st.metric("Total PnL", report["total_pnl"])
                st.write("Open Positions:", report["open_positions"])

            # Risk info
            with col2:
                st.header("⚠️ Risk")
                risk = self.risk_controller.report()
                st.metric("SafeMode", str(risk["safe_mode"]))
                st.metric("Drawdown", risk["drawdown"])
                st.metric("Loss Streak", risk["loss_streak"])
                st.metric("Error Count", risk["error_count"])

            # Orders
            with col3:
                st.header("📈 Open Orders")
                for order in self.execution_engine.open_orders:
                    st.write(order)

            # AI Engine status (optional)
            if self.ai_engine:
                st.subheader("🤖 AI Engine Status")
                # In thực tế nên show model info, last predict, conf threshold...
                st.write("Loaded Models:", list(self.ai_engine.models.keys()))

            # Last update time
            last_update.info(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')} (auto refresh {refresh_sec}s)")
            time.sleep(refresh_sec)
            st.experimental_rerun()

# Usage example/test
if __name__ == "__main__":
    from capital.capital_manager import CapitalManager
    from risk.risk_controller import RiskController
    from execution.execution_engine import ExecutionEngine
    from ai.ai_engine import AIEngine

    class DummyClient:
        def create_order(self, **kwargs): return {**kwargs, "id": 123}
        def update_stop_loss(self, order_id, sl): pass

    cm = CapitalManager()
    rc = RiskController()
    ee = ExecutionEngine(DummyClient(), cm, rc)
    ai = AIEngine()
    app = DashboardApp(cm, rc, ee, ai)
    # Nên chạy bằng: streamlit run src/dashboard/dashboard.py
    app.run()
