import os

os.environ.setdefault('APP_ENV', 'local')
os.environ.setdefault('DEBUG', 'true')
os.environ.setdefault('FLASK_APP', 'app:create_app')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '5000')
os.environ.setdefault('AI_SYSTEMS_ENABLED', 'false')
os.environ.setdefault('ENABLE_AUTOMATED_BACKUPS', 'false')

from app import create_app

application = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    application.run(host=host, port=port, debug=True)
