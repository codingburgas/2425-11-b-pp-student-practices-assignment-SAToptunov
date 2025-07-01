# run.py
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

# Създаваме инстанция на приложението
app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role}

@app.cli.command("create-roles")
def create_roles():
    """Създава ролите User и Admin в базата данни."""
    Role.insert_roles()
    print("Ролите 'User' и 'Admin' са създадени/проверени.")

# Това позволява да се стартира приложението директно с 'python run.py'
if __name__ == '__main__':
    app.run(debug=True)

