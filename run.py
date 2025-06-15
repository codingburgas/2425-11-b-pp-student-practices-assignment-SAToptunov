# run.py
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

# Създаваме инстанция на приложението
app = create_app()
migrate = Migrate(app, db)

# Това позволява да се стартира приложението директно с 'python run.py'
if __name__ == '__main__':
    app.run(debug=True)

# Добавяме контекст към flask shell за по-лесна работа
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)