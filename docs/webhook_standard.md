# 📘 webhook_standard.md

## 🔐 Cấu hình Webhook an toàn

### 1. Set ENV trong Railway / .env

```env
WEBHOOK_SECRET=abc123xyz
```

### 2. Gửi payload client

```python
import hmac, hashlib, json

payload = {
    "symbol": "BTC/USDT",
    "source": "tradingview",
    "action": "predict"
}

body = json.dumps(payload).encode("utf-8")
signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    body,
    hashlib.sha256
).hexdigest()
```

### 3. Server webhook validate

```python
import hmac, hashlib

def verify_signature(payload: str, sig: str, secret: str):
    mac = hmac.new(secret.encode(), payload.encode(), hashlib.sha256)
    return mac.hexdigest() == sig
```

## 🔁 Batch & Queue Cơ Chế

- Mỗi webhook trigger đưa vào queue đợi xử lý
- Queue xử lý tự động theo FIFO hoặc ưu tiên
- Có thể grouping batch signals

## 🔁 Feedback cho RL

- Nếu webhook gửi kèm `feedback` hoặc `reward`
  - Hệ thống sẽ update cho Reinforcement Trainer

```json
{
  "symbol": "ETH/USDT",
  "source": "appsheet",
  "action": "reward",
  "reward": 0.12
}
```

## 🧠 Khuyến nghị

- Luôn verify HMAC trước khi xử lý
- Dùng batch nếu webhook gửi liên tục
- Log webhook request để debug

