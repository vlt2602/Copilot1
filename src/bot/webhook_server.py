from flask import Flask, request, jsonify
import hmac, hashlib, os, json

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Signature')
    payload = request.data.decode('utf-8')
    mac = hmac.new(WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256)
    if mac.hexdigest() != signature:
        return 'Invalid signature', 403
    data = json.loads(payload)
    # TODO: Queue, batch, RL feedback
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(port=5000)
