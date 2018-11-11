from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager

from payment_service.wsgi import db, wsgi_app


migrate = Migrate(wsgi_app, db)
manager = Manager(wsgi_app)
manager.add_command('db', MigrateCommand)


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    manager.run()
