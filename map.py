from core.server import socketio, app

if __name__ == '__main__':
    socketio.run(app, debug=True)
