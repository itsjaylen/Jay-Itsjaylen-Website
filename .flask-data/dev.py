from flask import Flask
from views import app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8500, debug=True, use_reloader=False)