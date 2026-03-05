from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"

# --- Rutas hacia los JSON en la carpeta backend ---
BASE_DIR = os.path.dirname(__file__)  # carpeta frontend
USUARIOS_FILE = os.path.join(BASE_DIR, "..", "backend", "usuarios.json")
MENSAJES_FILE = os.path.join(BASE_DIR, "..", "backend", "mensajes.json")

# --- Funciones auxiliares ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_json(file):
    if not os.path.exists(file):
        # Inicializa usuarios como {} y mensajes como []
        with open(file, "w") as f:
            json.dump({} if file==USUARIOS_FILE else [], f)
    with open(file, "r") as f:
        return json.load(f)

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def registrar_usuario(username, email, password):
    usuarios = cargar_json(USUARIOS_FILE)
    if username in usuarios:
        return False
    usuarios[username] = {"email": email, "password": hash_password(password)}
    guardar_json(USUARIOS_FILE, usuarios)
    return True

def comprobar_usuario(username, password):
    usuarios = cargar_json(USUARIOS_FILE)
    return username in usuarios and usuarios[username]["password"] == hash_password(password)

def guardar_mensaje(autor, texto):
    mensajes = cargar_json(MENSAJES_FILE)
    mensajes.insert(0, {
        "autor": autor,
        "texto": texto,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    guardar_json(MENSAJES_FILE, mensajes)

def obtener_mensajes():
    return cargar_json(MENSAJES_FILE)

# --- Rutas Flask ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if comprobar_usuario(user, pwd):
            session["user"] = user
            return redirect("/wall")
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html", error=None)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        email = request.form["email"]
        if registrar_usuario(user, email, pwd):
            return redirect("/")
        else:
            return render_template("registro.html", error="Usuario ya existe")
    return render_template("registro.html", error=None)

@app.route("/wall", methods=["GET", "POST"])
def wall():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        texto = request.form["mensaje"]
        if texto.strip() != "":
            guardar_mensaje(session["user"], texto)
    return render_template("muro.html", mensajes=obtener_mensajes(), username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
    