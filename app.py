from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
from redis_config import r
from auth import auth_bp
import eventlet

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    all_rooms = list(r.smembers("chat_rooms"))
    if request.method == 'POST':
        room = request.form['room']
        return redirect(url_for('chat', room_name=room))
    return render_template('rooms.html', rooms=all_rooms)

@app.route('/chat/<room_name>')
def chat(room_name):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('chat.html', username=session['username'], room=room_name)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    r.sadd("chat_rooms", room)
    join_room(room)
    emit('message', {'username': 'System', 'msg': f'{username} joined the room'}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    emit('message', {'username': data['username'], 'msg': data['msg']}, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
