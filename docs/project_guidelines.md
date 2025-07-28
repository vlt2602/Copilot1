# 📘 project_guidelines.md

## 🧭 Tiêu chí dự án THopper PRO++

Tất cả các đề xuất, điều chỉnh logic, config hoặc code backend cần tuân theo tiêu chỉ chính sau:

- 🤖 **Thông minh**: ra quyết định nhanh, đầy đủ dữ liệu và logic
- ⚡️ **An toàn**: giới hạn rủi ro, SafeMode khi lỗi hoặc lỗi AI
- 💰 **Sinh lời tốt**: dựa trên risk-adjusted PnL
- ⌛ **Ổn định lâu dài**: hoạt động bền vững theo thời gian
- 💸 **Tiết kiệm chi phí vận hành**: không cần server đặc thù

## ✅ Checklist khi build/update

| Module               | Câu hỏi kiểm tra                                                            |
|----------------------|--------------------------------------------------------------------------------------|
| Pipeline             | Đã chia đủ 7 lớp? Giữ df cũ, không fetch toàn bộ?                  |
| AI Trainer           | Mô hình tự train theo nến mới? Chuẩn hóa input/output?                         |
| Capital Manager      | Tính vốn linh hoạt, scaling với pyramiding, report PnL?                       |
| Risk Controller      | SafeMode hoạt động? Về logic và về Telegram/Discord?                       |
| Discord Bot          | Slash Command đã đủ? Nhận lệnh tay + webhook?                            |
| Webhook Server       | Đã có HMAC-SHA256? Hỗ trợ retry queue + batch?                           |
| Dashboard            | Streamlit tổng quan? Có PnL, status, log?                                  |
| Logging              | Dùng LogManager? Tách log theo module? Có log AI, signal, order?                     |
| Model Storage        | models/ giữ đẹp? Có cache hay checkpoint cho LSTM/RL?                 |
| Config Loader        | Tách bỏ hardcode? Load YAML chuẩn hóa?                                      |

## 🆘 Auto SafeMode khi gặp lỗi

- Các trường hợp kick SafeMode:
  - ❌ AI predict fail hoặc vắng
  - ⚡️ Lỗi liên tiếp trong 2 chu kỳ (nến)
  - ⬆️ Giao dịch thua liên tiếp 3 lệnh
  - 🌪 Biến động thị trường tăng đột ngột (ATR cao)

- Khi SafeMode:
  - Ngắt ngay giao dịch mới trong 60 phút
  - Chỉ gửi lệnh khi đã khởi phục
  - Ghi log SafeMode và báo cáo vào Discord log

## ✨ Khối lượng khuyến nghị

| Loại dữ liệu   | Khuyến nghị max candles/timeframe |
|----------------|-----------------------------|
| XGBoost        | 1000                         |
| LSTM           | 3000                         |
| RL             | 600                          |
| Tổng df     | max 4000, xóa bớ 1000 nến cũ nhất khi vượt |

## 🪜 Chiến lược đã tích hợp thêm:

- `dca_breakout` (DCA logic cho breakout)
- `copy_trade` (chỉ hoạt động khi follower.yaml được set)
- `trailing_pnl` hoặc `trailing_atr` (stop loss theo TSL)
- Reward mode cho RL: `pnl_gain` hoặc `signal_accuracy`

