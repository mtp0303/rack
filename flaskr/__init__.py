from flask import Flask

def create_app():
    app = Flask(__name__)

    from .control import main, room, modal, alarm, department

    app.register_blueprint(main.bp)
    app.register_blueprint(room.bp)
    app.register_blueprint(modal.bp)
    app.register_blueprint(alarm.bp)
    app.register_blueprint(department.bp)

    return app