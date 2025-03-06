from flask import Flask, request, jsonify
from database import add_subscriber, remove_subscriber, get_subscribers

app = Flask(__name__)

@app.route('/subscribe', methods=['POST'])
def subscribe_user():
    """Subscribe a user to receive signals."""
    data = request.json
    chat_id = data.get("chat_id")

    if not chat_id:
        return jsonify({"error": "chat_id is required"}), 400

    add_subscriber(chat_id)
    return jsonify({"message": f"User {chat_id} subscribed successfully"}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe_user():
    """Unsubscribe a user from receiving signals."""
    data = request.json
    chat_id = data.get("chat_id")

    if not chat_id:
        return jsonify({"error": "chat_id is required"}), 400

    remove_subscriber(chat_id)
    return jsonify({"message": f"User {chat_id} unsubscribed successfully"}), 200

@app.route('/subscribers', methods=['GET'])
def list_subscribers():
    """Get all subscribed users."""
    subscribers = get_subscribers()
    return jsonify({"subscribers": subscribers}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
