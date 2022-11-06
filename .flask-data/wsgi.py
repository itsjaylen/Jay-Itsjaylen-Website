from flask import Flask
from views import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False)
    
    "gunicorn -w 4 -b 0.0.0.0 -b :8001 'views:app'"
    
    "gunicorn views:app -b :8001"
    "gunicorn views:app -b :8001"
    
    """
    gunicorn -w 4 -b 0.0.0.0:8001 'views:app'
    """