# 🚀 THopper PRO++ – AI Crypto Trading System

THopper PRO++ là hệ thống giao dịch crypto tự động dùng AI, hỗ trợ nhiều chiến lược, quản lý rủi ro thông minh, trigger linh hoạt (candle, webhook, Discord, dashboard). Triển khai dễ dàng trên Railway, Docker, hoặc VPS.

## 🌟 Tính năng chính
- Giao dịch tự động DCA, breakout, copytrade, trailing SL/TP
- Quản lý rủi ro thông minh với SafeMode tự động
- AI đa mô hình (XGBoost, LSTM, RL), tự train, tự tối ưu
- Báo cáo PnL daily qua Discord, dashboard Streamlit
- Trigger qua webhook chuẩn HMAC-SHA256, Discord Slash Command

## 🔧 Yêu cầu hệ thống
- Python >= 3.10
- Railway/Docker/VPS
- Biến môi trường cấu hình trong `.env`

## 📁 Cấu trúc dự án
```bash
THopper/
├── config/
├── models/
├── scripts/
├── src/
│   ├── ai/
│   ├── risk/
│   ├── pipeline/
│   ├── bot/
│   ├── dashboard/
│   ├── utils/
│   └── main.py
├── tests/
├── .env.example
├── Dockerfile
├── Procfile
├── README.md
```

## ▶️ Khởi chạy dự án
1. Cài đặt Python & pipenv/venv
2. Tạo file `.env` dựa trên `.env.example`
3. Cài đặt dependencies: `pip install -r requirements.txt`
4. Khởi chạy bot: `python src/main.py --bot`
5. Khởi chạy dashboard: `streamlit run src/dashboard/dashboard.py`

---

## 📚 Tài liệu chi tiết
- [docs/discord_commands.md](docs/discord_commands.md)
- [docs/project_guidelines.md](docs/project_guidelines.md)
- [docs/strategy_config_format.md](docs/strategy_config_format.md)
- [docs/webhook_standard.md](docs/webhook_standard.md)

## 🧪 Test & CI/CD
- `pytest tests/`
- Script test AI: `python scripts/unit_test_ai.py`
