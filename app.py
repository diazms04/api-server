from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import socket

app = Flask(__name__)

# Conexión a PostgreSQL (LOCAL por ahora)
# Luego este mismo string será el de RDS
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://martin@localhost:5432/flaskdb"
)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modelo
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


# Crear tablas automáticamente (Flask 2.3+)
with app.app_context():
    db.create_all()


# Health check (ideal para ALB)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "host": socket.gethostname()
    })


# Listar usuarios
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "name": u.name} for u in users
    ])


# Crear usuario
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    user = User(name=data["name"])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "id": user.id,
        "name": user.name
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2300)