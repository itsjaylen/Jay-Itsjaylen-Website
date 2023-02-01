# wsgi.py

from app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=7000, host="0.0.0.0", use_reloader=True)
    # socketio.run(app, debug=True, port=7000, host="0.0.0.0")
