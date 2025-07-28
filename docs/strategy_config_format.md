# 📘 strategy_config.md

## 🧠 AI Config

```yaml
xgb:
  threshold: 0.6
  candle_limit: 1000

lstm:
  threshold: 0.7
  candle_limit: 3000

rl:
  candle_limit: 600
reward_mode: pnl_gain
```

## 📊 Data Fetcher

```yaml
data_fetcher:
  max_candles: 4000
```

- Khi vượt 4000 nến/thời gian → xóa bớ 1000 nến cũ nhất

## ⚙️ Strategy Template

```yaml
strategy:
  name: rsi_macd
  timeframe: 1h
  version: '1.5-stable'
  min_p_buy: 0.25
  confidence_threshold: 0.70
  allowed_side: [buy, sell]
  use_trend_filter: true

  dynamic_sl_tp: true
  sl: 2.5
  tp: 5.0

  trailing:
    enabled: true
    type: pnl
    trigger_pct: 1.5
    trail_pct: 0.4

  min_volume_binance: 25000000
  top_n: 20
  max_workers: 20
  debug: true

  banned_keywords:
    - DOWN
    - UP
    - BULL
    - BEAR
    - TUSD
```

## 💡 Chiến lược mở rộng (advanced)

```yaml
available_strategies:
  - rsi_macd
  - breakout_vwap
  - mean_reversion
  - trend_breakout
  - dca_breakout

coin_filter_advanced:
  enabled: true
  min_buy_volume_usdt_15m: 4000000
  min_buy_volume_usdt_1h: 8000000
  prefer_buy_ratio: 6.0
  exclude_if_sell_ratio: 2.0
```

## 🔁 CopyTrade YAML (nếu dùng)

```yaml
copy_trade:
  mode: mirror
  followers:
    - user1: APIKEY123
    - user2: APIKEY456
```

## 🔒 SafeMode logic

```yaml
risk_control:
  enable_safe_mode: true
  safe_mode_trigger:
    - ai_error
    - continuous_loss
    - high_atr_spike
    - system_crash
  disable_after_minutes: 60
```

## 📆 Report

```yaml
daily_report:
  enable: true
  send_time_utc: "00:15"
```

