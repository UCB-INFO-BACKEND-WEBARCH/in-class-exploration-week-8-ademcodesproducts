"""
Notification Service API - Starter (Synchronous)

This version sends notifications SYNCHRONOUSLY.
Each request blocks for 3 seconds while "sending" the notification.

YOUR TASK: Convert this to use rq for background processing!
"""

from flask import Flask, jsonify, request
import uuid
import os
from redis import Redis
from tasks import send_notification

app = Flask(__name__)

redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# In-memory store for notifications
notifications = {}


@app.route('/')
def index():
    return jsonify({
        "service": "Notification Service (Async - Fast!)",
        "endpoints": {
            "POST /notifications": "Queue a notification (returns instantly!)",
            "GET /notifications": "List all notifications",
            "GET /notifications/<id>": "Get a notification"
        }
    })


@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400

    notification_id = str(uuid.uuid4())
    email = data['email']
    message = data.get('message', 'You have a new notification!')

    job = send_notification.delay(notification_id, email, message)

    return jsonify({"job_id": job.id}), 202


@app.route('/notifications', methods=['GET'])
def list_notifications():
    """List all notifications."""
    return jsonify({
        "notifications": list(notifications.values())
    })


@app.route('/notifications/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    """Get a single notification."""
    notification = notifications.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify(notification)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
