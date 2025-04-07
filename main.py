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
    buy_limit = data.get("buy_limit", "N/A")
    
    try:
        entry = float(buy_limit)
    except:
        return jsonify({"error": "Invalid entry price"}), 400

    # PIP Style for GOLD (1 pip = 0.10)
    pip_value = 0.10

    # === Auto-Calculated SL / TP / Zone
    sl = entry - (30 * pip_value)
    tp1 = entry + (30 * pip_value)
    tp2 = entry + (50 * pip_value)
    tp3 = entry + (70 * pip_value)
    top_zone = entry + (10 * pip_value)
    bottom_zone = entry - (10 * pip_value)

    # Pip Calculations
    sl_pips = round(abs(entry - sl) / pip_value)
    tp1_pips = round(abs(tp1 - entry) / pip_value)
    tp2_pips = round(abs(tp2 - entry) / pip_value)
    tp3_pips = round(abs(tp3 - entry) / pip_value)

    # Emoji Logic
    if "bearish" in signal_type.lower():
        emoji = "🔴"
    else:
        emoji = "🟢"

    # Final Message
    signal_message = f"""
🔔*VESSA HAVE SIGNAL FOR YOU*🔔

{emoji} Vessa {signal_type} detected {emoji}
💰 *Entry:* {entry:.2f}  
📍 Top Zone: {top_zone:.2f}  
📍 Bottom Zone: {bottom_zone:.2f}  
🚫 *Stop Loss:* {sl:.2f} (-{sl_pips} pip)  
🎯 *Take Profit 1:* {tp1:.2f} (+{tp1_pips} pip)  
🎯 *Take Profit 2:* {tp2:.2f} (+{tp2_pips} pip)  
🎯 *Take Profit 3:* {tp3:.2f} (+{tp3_pips} pip)

🧠 *Powered by VESSA AI Agent*
"""

    # Send to all subscribers
    subscribers = get_subscribers(instrument)
    if not subscribers:
        return jsonify({"message": f"No subscribers for {instrument}"}), 200

    for chat_id in subscribers:
        send_telegram_message(chat_id, signal_message)

    return jsonify({"message": f"Signal sent to {len(subscribers)} subscribers", "subscribers": subscribers}), 200

# === Launch
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
