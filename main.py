import os
import requests
from flask import Flask, request, jsonify
from database import add_subscriber, remove_subscriber, get_subscribers

app = Flask(__name__)

# ✅ Telegram Bot Token from Railway ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")


def send_telegram_message(chat_id, message):
    """Send a message to a Telegram user."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

# === Health Check ===
@app.route('/')
def home():
    return "VESSA Webhook is running!", 200

@app.route('/routes')
def list_routes():
    return jsonify([str(rule) for rule in app.url_map.iter_rules()])

# === Subscribe API ===
@app.route('/subscribe', methods=['POST'])
def subscribe_user():
    data = request.json
    chat_id = data.get("chat_id")
    instrument = data.get("instrument")
    if not chat_id or not instrument:
        return jsonify({"error": "chat_id and instrument are required"}), 400
    add_subscriber(chat_id, instrument)
    return jsonify({"message": f"User {chat_id} subscribed to {instrument}"}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe_user():
    data = request.json
    chat_id = data.get("chat_id")
    instrument = data.get("instrument")
    if not chat_id or not instrument:
        return jsonify({"error": "chat_id and instrument are required"}), 400
    remove_subscriber(chat_id, instrument)
    return jsonify({"message": f"User {chat_id} unsubscribed from {instrument}"}), 200

@app.route('/subscribers', methods=['GET'])
def list_subscribers():
    instrument = request.args.get("instrument")
    if not instrument:
        return jsonify({"error": "instrument is required"}), 400
    subscribers = get_subscribers(instrument)
    return jsonify({"subscribers": subscribers}), 200

# === Webhook Signal from TradingView ===
@app.route('/webhook', methods=['POST'])
def receive_signal():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Extract from JSON
    instrument = data.get("instrument", "Unknown")
    signal_type = data.get("signal", "No signal provided")
    top_zone = data.get("top_zone", "N/A")
    bottom_zone = data.get("bottom_zone", "N/A")
    buy_limit = data.get("buy_limit", "N/A")
    stop_loss = data.get("stop_loss", "N/A")
    take_profit1 = data.get("tp1", "N/A")
    take_profit2 = data.get("tp2", "N/A")
    take_profit3 = data.get("tp3", "N/A")

    subscribers = get_subscribers(instrument)
    if not subscribers:
        return jsonify({"message": f"No subscribers for {instrument}"}), 200

    # ✅ VESSA Message Format
    signal_message = f"""
📢 *VESSA TRADING SIGNAL ALERT* 📢

🚀 *{instrument.upper()} SIGNAL FOR SUBSCRIBERS* 🚀

🟢 {signal_type} detected 🟢
*Top Zone:* {top_zone}  
*Bottom Zone:* {bottom_zone}  

💰 *Buy Limit:* {buy_limit}  
❌ *Stop Loss:* {stop_loss}  
🎯 *Take Profit 1:* {take_profit1}  
🎯 *Take Profit 2:* {take_profit2}  
🎯 *Take Profit 3:* {take_profit3}  
"""

    for chat_id in subscribers:
        send_telegram_message(chat_id, signal_message)

    return jsonify({"message": f"Signal sent to {len(subscribers)} subscribers", "subscribers": subscribers}), 200

# === Launch
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
