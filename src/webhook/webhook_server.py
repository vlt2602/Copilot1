import hmac
import hashlib
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager

class WebhookQueue:
    """
    Hàng đợi xử lý lệnh/batch từ webhook, cho phép các worker lấy lệnh ra xử lý.
    """
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def put(self, payload):
        with self.lock:
            self.queue.append(payload)

    def get(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            return None

    def size(self):
        with self.lock:
            return len(self.queue)

class WebhookHandler(BaseHTTPRequestHandler):
    """
    HTTP Handler nhận webhook, verify HMAC, push vào queue.
    """
    queue = None
    secret = ""
    logger = None
    reward_callback = None

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(length)
        sig = self.headers.get("X-Hub-Signature", "")

        # Verify HMAC nếu có secret
        if self.secret:
            computed_sig = "sha256=" + hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, computed_sig):
                self.send_response(401)
                self.end_headers()
                self.logger.warning("HMAC signature mismatch!")
                return

        try:
            data = json.loads(body)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.logger.warning(f"JSON decode error: {e}")
            return

        # Nếu là reward RL, gọi callback luôn (không queue)
        if data.get("type") == "reward" and self.reward_callback:
            self.reward_callback(data)
            self.send_response(200)
            self.end_headers()
            self.logger.info("RL reward received and processed.")
            return

        # Đưa vào hàng đợi
        self.queue.put(data)
        self.send_response(200)
        self.end_headers()
        self.logger.info(f"Webhook received and queued: {data.keys()}")

    def log_message(self, format, *args):
        # Ghi log về hệ thống logging, không in ra stdout
        self.logger.debug(format % args)

class WebhookServer:
    """
    Webhook HTTP server chạy nền, nhận tín hiệu ngoài và phân phối tới pipeline.
    """
    def __init__(self, queue, secret="", reward_callback=None, port=8088):
        self.queue = queue
        self.secret = secret
        self.port = port
        self.reward_callback = reward_callback
        self.logger = LogManager.get_logger("webhook")

        # Gán static biến cho Handler
        WebhookHandler.queue = self.queue
        WebhookHandler.secret = self.secret
        WebhookHandler.logger = self.logger
        WebhookHandler.reward_callback = self.reward_callback

        self.httpd = HTTPServer(('0.0.0.0', self.port), WebhookHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self):
        self.logger.info(f"Starting Webhook server at port {self.port}")
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping Webhook server...")
        self.httpd.shutdown()
        self.thread.join()

# Usage example/test
if __name__ == "__main__":
    def reward_callback(data):
        print("RL reward received:", data)

    queue = WebhookQueue()
    config = ConfigLoader()
    secret = config.get("webhook", reload=True).get("secret", "")
    port = int(config.get("webhook", reload=True).get("port", 8088))
    server = WebhookServer(queue, secret, reward_callback, port)
    server.start()
    print(f"Webhook server is running at http://0.0.0.0:{port}/ ... Press Ctrl+C to stop.")

    try:
        while True:
            payload = queue.get()
            if payload:
                print("Processing payload:", payload)
    except KeyboardInterrupt:
        server.stop()
