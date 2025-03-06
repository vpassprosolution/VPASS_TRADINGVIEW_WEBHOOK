import requests
from flask import Flask, request, jsonify
from database import get_subscribers

app = Flask(__name__)

# Telegram Bot Token (Replace with your bot's token)
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

    # Get all subscribed users
    subscribers = get_subscribers()

    if not subscribers:
        return jsonify({"message": "No subscribers to send the signal to."}), 200

    # Send message to each subscriber via Telegram
    for chat_id in subscribers:
        send_telegram_message(chat_id, signal_message)

    return jsonify({"message": "Signal sent to subscribers", "subscribers": subscribers}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
