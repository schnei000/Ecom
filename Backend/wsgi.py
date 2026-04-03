import os
from dotenv import load_dotenv
from app import create_app

# Charger variables d'environnement
load_dotenv()

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.getenv('SERVER_HOST', '127.0.0.1')
    port = int(os.getenv('SERVER_PORT', 5000))
    app.run(port=port, host=host, debug=debug)
