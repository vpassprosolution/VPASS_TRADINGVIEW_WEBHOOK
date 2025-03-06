import os
import requests
from flask import Flask, request, jsonify
from database import add_subscriber, remove_subscriber, get_subscribers

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"

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

# === Health Check and Debug Routes ===
@app.route('/')
def home():
    """Health check endpoint to confirm Flask is running."""
    return "VPASS Webhook is running!", 200

@app.route('/routes')
def list_routes():
    """List all available API routes for debugging."""
    return jsonify([str(rule) for rule in app.url_map.iter_rules()])

# === Subscription API Endpoints (Fixed to Track Instruments) ===
@app.route('/subscribe', methods=['POST'])
def subscribe_user():
    """Subscribe a user to a specific instrument."""
    data = request.json
    chat_id = data.get("chat_id")
    instrument = data.get("instrument")

    if not chat_id or not instrument:
        return jsonify({"error": "chat_id and instrument are required"}), 400

    add_subscriber(chat_id, instrument)
    return jsonify({"message": f"User {chat_id} subscribed to {instrument} successfully"}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe_user():
    """Unsubscribe a user from a specific instrument."""
    data = request.json
    chat_id = data.get("chat_id")
    instrument = data.get("instrument")

    if not chat_id or not instrument:
        return jsonify({"error": "chat_id and instrument are required"}), 400

    remove_subscriber(chat_id, instrument)
    return jsonify({"message": f"User {chat_id} unsubscribed from {instrument} successfully"}), 200

@app.route('/subscribers', methods=['GET'])
def list_subscribers():
    """Get all subscribed users for a specific instrument."""
    instrument = request.args.get("instrument")

    if not instrument:
        return jsonify({"error": "instrument is required"}), 400

    subscribers = get_subscribers(instrument)
    return jsonify({"subscribers": subscribers}), 200

# === TradingView Webhook Endpoint ===
@app.route('/webhook', methods=['POST'])
def receive_signal():
    """Receive TradingView signals and send only to subscribed users."""
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    # Extract signal data
    instrument = data.get("instrument", "Unknown")
    signal_type = data.get("signal", "No signal provided")
    top_zone = data.get("top_zone", "N/A")
    bottom_zone = data.get("bottom_zone", "N/A")
    buy_limit = data.get("buy_limit", "N/A")
    stop_loss = data.get("stop_loss", "N/A")
    take_profit1 = data.get("tp1", "N/A")
    take_profit2 = data.get("tp2", "N/A")
    take_profit3 = data.get("tp3", "N/A")

    # Format the signal message
    signal_message = f"""
📢 *VPASS TRADING SIGNAL ALERT* 📢

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

    # Get all subscribed users for this specific instrument
    subscribers = get_subscribers(instrument)

    if not subscribers:
        return jsonify({"message": "No subscribers to send the signal to."}), 200

    # Send message to each subscriber via Telegram
    for chat_id in subscribers:
        send_telegram_message(chat_id, signal_message)

    return jsonify({"message": "Signal sent to subscribers", "subscribers": subscribers}), 200

# === Run Flask App ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Railway-assigned port if available
    app.run(host='0.0.0.0', port=port, debug=True)
