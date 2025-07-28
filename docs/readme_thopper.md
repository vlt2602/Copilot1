# 📘 README\_THopper.md

## 🚀 Giới thiệu

**THopper PRO++** là hệ thống giao dịch AI crypto thông minh, realtime, có khả năng phản ứng nhanh với thị trường thông qua trigger nến mới, webhook ngoài và điều khiển bằng Discord Bot. Toàn bộ hệ thống được triển khai theo kiến trúc monorepo, tối ưu chi phí vận hành và có thể triển khai dễ dàng trên Railway.

## 🔧 Yêu cầu hệ thống

- Python >= 3.10
- Railway hoặc VPS hỗ trợ Docker / Procfile

## 📁 Cấu trúc thư mục chính

```bash
THopper/
├── config/            # Cấu hình chiến lược, AI, risk
├── models/            # Lưu mô hình đã train
├── scripts/           # Chạy pipeline, test, khởi động
├── tests/             # Tập test CI/CD
├── src/               # Toàn bộ source code chia module
├── pipeline.py        # Gọi toàn bộ 7 lớp pipeline
├── main.py            # Điều phối khởi động bot + pipeline
├── Procfile           # Railway định nghĩa web / worker
├── Dockerfile         # Tùy chọn nếu dùng VPS
├── .env.example       # Biến môi trường mẫu
```

## 🧠 Mô hình AI

- **XGBoost** → Trigger khi có nến 15m mới
- **LSTM** → Trigger khi có nến 1h mới
- **RL (Reinforcement Learning)** → Trigger sau lệnh hoặc từ Webhook
- Hỗ trợ multi-timeframe: 15m, 1h, 4h
- Output chuẩn hóa: `ScoredSignal`

## 📥 Dữ liệu & cơ chế nến

- Khi chạy lần đầu: tải toàn bộ dữ liệu cần thiết và train mô hình tương ứng
- Sau đó, mỗi khi có nến mới → chỉ tải bổ sung (append)
- Tổng số nến không vượt quá **4000 nến/timeframe**
  - Nếu vượt → tự động xoá **1000 nến cũ nhất** để giữ hiệu suất và tiết kiệm bộ nhớ

## 🔁 Trigger Hệ thống

| Nguồn Trigger         | Mô tả                            |
| --------------------- | -------------------------------- |
| Scheduler             | (Tùy chọn) 15m/lần               |
| Webhook               | Từ TradingView, Sheets, AppSheet |
| Discord Slash Command | Điều khiển bằng tay              |
| Dashboard             | Qua Streamlit UI                 |
| Nến mới               | Realtime listener 15m/1h/4h      |

## 🤖 Slash Command Discord (chuẩn)

| Lệnh                        | Chức năng                                |
| --------------------------- | ---------------------------------------- |
| `/start`                    | Khởi động pipeline                       |
| `/stop`                     | Dừng pipeline                            |
| `/status`                   | Kiểm tra trạng thái module               |
| `/signal [symbol]`          | Xem tín hiệu mới nhất                    |
| `/buy [symbol] [amount]`    | Mua thủ công                             |
| `/sell [symbol] [amount]`   | Bán thủ công                             |
| `/retrain [symbol?]`        | Retrain AI thủ công (toàn bộ hoặc 1 cặp) |
| `/logs [type]`              | Lấy log theo loại (ai/order/signal)      |
| `/safe_mode enable/disable` | Bật tắt SafeMode                         |
| `/dashboard`                | Gửi link dashboard                       |
| `/daily_report`             | Gửi báo cáo PnL/ngày về Discord          |

## 🔐 Webhook chuẩn HMAC-SHA256

1. Set biến môi trường `WEBHOOK_SECRET`
2. Client ký payload bằng SHA256:

```python
import hmac, hashlib, json
body = json.dumps(payload).encode("utf-8")
signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
```

3. Server xác minh `signature`

## 🔄 Các tính năng tương đương hoặc nâng cấp từ CryptoHopper Hero

- ✅ Giao dịch DCA (`dca_breakout` strategy)
- ✅ CopyTrade theo `leader.json` → follower mirror/fixed
- ✅ Quản lý trailing SL/TP động (pnl hoặc atr)
- ✅ Pyramiding (scaling position theo tín hiệu)
- ✅ Báo cáo tự động `/daily_report`
- ✅ Webhook mở rộng: retry queue, batch signal
- ✅ Dashboard công khai (không cần app riêng)
- ✅ Tự động SafeMode khi lỗi liên tục

## 🧪 Test & CI/CD

```bash
pytest tests/              # Test toàn hệ thống
python scripts/unit_test_ai.py   # Test AI input/output
```

## ▶️ Khởi chạy

**Chạy local:**

```bash
python main.py --bot        # Chạy bot + pipeline
```

**Trên Railway:**

```
Procfile:
web: streamlit run src/dashboard/ci_cd_dashboard.py --server.port $PORT
worker: python3 main.py --bot
```

---

## 🧠 Ghi chú

- Luôn giữ df đã fetch, chỉ thêm nến mới
- `LogManager` thay thế mọi `print()`
- Tất cả config qua `ConfigLoader`, không hardcode
- Hệ thống chuẩn hóa chuẩn THopper PRO++
- Tự động chuyển sang SafeMode nếu lỗ liên tục hoặc thị trường biến động mạnh
- Gửi báo cáo `/daily_report` mỗi ngày nếu bật tính năng này

