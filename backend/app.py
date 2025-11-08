"""
Backend server for Elderly Voice Agent
Handles messaging, calls, and notifications
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from messaging_service import MessagingService
from call_service import CallService
from notification_service import NotificationService

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize services
messaging_service = MessagingService()
call_service = CallService()
notification_service = NotificationService()

# Store connected clients (user_id -> session_id)
connected_clients = {}
# Simple helper to log function/tool calls
def log_tool_call(action: str, payload: dict):
    try:
        marker = request.headers.get('X-LLM-Function') or action
    except Exception:
        marker = action
    ts = datetime.now().isoformat()
    try:
        body = json.dumps(payload, ensure_ascii=False)
    except Exception:
        body = str(payload)
    ip = None
    try:
        ip = request.remote_addr
    except Exception:
        ip = "unknown"
    print(f"[BACKEND][{ts}] {marker} from {ip} payload={body}")


@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "service": "Elderly Voice Agent Backend",
        "version": "1.0.0"
    })


# ============== Messaging API ==============

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send a text message to a contact"""
    try:
        data = request.json
        contact = data.get('contact')
        message = data.get('message')
        sender = data.get('sender', 'user')

        log_tool_call('send_message', {
            'contact': contact,
            'message': message,
            'sender': sender
        })

        if not contact or not message:
            return jsonify({"status": "error", "message": "Missing contact or message"}), 400

        # Send message through messaging service
        result = messaging_service.send_message(sender, contact, message)

        if result['success']:
            # Notify recipient via WebSocket if they're connected
            if contact in connected_clients:
                socketio.emit('new_message', {
                    'from': sender,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }, room=connected_clients[contact])

            return jsonify({"status": "success", "message_id": result['message_id']}), 200
        else:
            return jsonify({"status": "error", "message": result['error']}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/messages/history', methods=['GET'])
def get_message_history():
    """Get message history with a contact"""
    try:
        contact = request.args.get('contact')
        user = request.args.get('user', 'user')
        limit = int(request.args.get('limit', 50))

        log_tool_call('get_message_history', {
            'contact': contact,
            'user': user,
            'limit': limit
        })

        if not contact:
            return jsonify({"status": "error", "message": "Missing contact parameter"}), 400

        messages = messaging_service.get_history(user, contact, limit)
        return jsonify({"status": "success", "messages": messages}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============== Call API ==============

@app.route('/api/calls/request', methods=['POST'])
def request_call():
    """Request a voice or video call"""
    try:
        data = request.json
        contact = data.get('contact')
        call_type = data.get('type', 'voice')  # 'voice' or 'video'
        caller = data.get('caller', 'user')

        log_tool_call('request_call', {
            'contact': contact,
            'type': call_type,
            'caller': caller
        })

        if not contact:
            return jsonify({"status": "error", "message": "Missing contact"}), 400

        if call_type not in ['voice', 'video']:
            return jsonify({"status": "error", "message": "Invalid call type"}), 400

        # Create call request
        result = call_service.create_call(caller, contact, call_type)

        if result['success']:
            call_id = result['call_id']

            # Notify recipient via WebSocket
            if contact in connected_clients:
                socketio.emit('incoming_call', {
                    'call_id': call_id,
                    'from': caller,
                    'type': call_type,
                    'timestamp': datetime.now().isoformat()
                }, room=connected_clients[contact])

            return jsonify({
                "status": "success", 
                "call_id": call_id,
                "room_url": result.get('room_url')
            }), 200
        else:
            return jsonify({"status": "error", "message": result['error']}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/calls/respond', methods=['POST'])
def respond_to_call():
    """Accept or reject an incoming call"""
    try:
        data = request.json
        call_id = data.get('call_id')
        accept = data.get('accept', False)
        user = data.get('user', 'user')

        log_tool_call('respond_to_call', {
            'call_id': call_id,
            'accept': accept,
            'user': user
        })

        if not call_id:
            return jsonify({"status": "error", "message": "Missing call_id"}), 400

        if accept:
            # Accept the call
            result = call_service.accept_call(call_id, user)

            if result['success']:
                # Notify caller that call was accepted
                call_info = call_service.get_call_info(call_id)
                caller = call_info['caller']

                if caller in connected_clients:
                    socketio.emit('call_accepted', {
                        'call_id': call_id,
                        'room_url': result['room_url'],
                        'timestamp': datetime.now().isoformat()
                    }, room=connected_clients[caller])

                return jsonify({
                    "status": "success",
                    "room_url": result['room_url']
                }), 200
            else:
                return jsonify({"status": "error", "message": result['error']}), 500
        else:
            # Reject the call
            result = call_service.reject_call(call_id, user)

            if result['success']:
                # Notify caller that call was rejected
                call_info = call_service.get_call_info(call_id)
                caller = call_info['caller']

                if caller in connected_clients:
                    socketio.emit('call_rejected', {
                        'call_id': call_id,
                        'timestamp': datetime.now().isoformat()
                    }, room=connected_clients[caller])

                return jsonify({"status": "success"}), 200
            else:
                return jsonify({"status": "error", "message": result['error']}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/calls/end', methods=['POST'])
def end_call():
    """End an active call"""
    try:
        data = request.json
        call_id = data.get('call_id')

        log_tool_call('end_call', {
            'call_id': call_id
        })

        if not call_id:
            return jsonify({"status": "error", "message": "Missing call_id"}), 400

        result = call_service.end_call(call_id)

        if result['success']:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": result['error']}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============== WebSocket Events ==============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'status': 'success'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

    # Remove from connected clients
    for user_id, session_id in list(connected_clients.items()):
        if session_id == request.sid:
            del connected_clients[user_id]
            break


@socketio.on('register')
def handle_register(data):
    """Register a user with their session ID"""
    user_id = data.get('user_id')
    if user_id:
        connected_clients[user_id] = request.sid
        join_room(user_id)
        emit('registered', {'status': 'success', 'user_id': user_id})
        print(f"User {user_id} registered with session {request.sid}")


@socketio.on('unregister')
def handle_unregister(data):
    """Unregister a user"""
    user_id = data.get('user_id')
    if user_id and user_id in connected_clients:
        leave_room(user_id)
        del connected_clients[user_id]
        emit('unregistered', {'status': 'success'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
