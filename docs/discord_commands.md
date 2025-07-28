# 📘 discord_commands.md

## 🤖 Lệnh Slash cho THopper PRO++

### 🔄 Pipeline & Trạng thái

| Lệnh        | Mô tả                                                |
|---------------|---------------------------------------------------------|
| `/start`      | Khởi động pipeline toàn bộ                               |
| `/stop`       | Dừng pipeline (không thoát bot)                           |
| `/status`     | Kiểm tra trạng thái các module                          |

### 📈 Tín hiệu và AI

| Lệnh                  | Mô tả                                             |
|-------------------------|--------------------------------------------------|
| `/signal [symbol]`      | Lấy tín hiệu AI mới nhất cho symbol                |
| `/retrain [symbol?]`    | Retrain AI cho symbol (hoặc tất cả nếu không nhập) |
| `/logs [type]`          | Log theo module: ai, order, signal                |

### 💸 Giao dịch thủ công

| Lệnh                    | Mô tả                          |
|---------------------------|-------------------------------|
| `/buy [symbol] [amount]`  | Lệnh mua ngay lập tức         |
| `/sell [symbol] [amount]` | Lệnh bán ngay lập tức         |

### 🚫 SafeMode

| Lệnh                        | Mô tả                                  |
|-------------------------------|-------------------------------------------|
| `/safe_mode enable`          | Bật SafeMode                          |
| `/safe_mode disable`         | Tắt SafeMode                         |

### 📈 Dashboard & Báo cáo

| Lệnh               | Mô tả                                  |
|----------------------|-------------------------------------------|
| `/dashboard`         | Gửi link dashboard                     |
| `/daily_report`      | Gửi báo cáo PnL/ngày qua Discord        |

