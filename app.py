"""
Escape Room de Ciberseguridad - Cyber Bomb
Aplicación principal Flask
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils.crypto import decrypt_caesar
import secrets
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuración del juego
INITIAL_TIME = 600  # 10 minutos en segundos
INITIAL_HINTS = 3
TIME_BONUS = 30  # segundos por nivel completado
HINT_PENALTY = 10  # segundos por pista usada

# Definición de niveles
LEVELS = [
    {
        "type": "password",
        "title": "Contraseña Débil",
        "prompt": "Ingresa la contraseña del administrador del sistema.",
        "solution": "1234",
        "hint": "El admin nunca cambia su clave… empieza con 1."
    },
    {
        "type": "phishing",
        "title": "Caza-Phish",
        "prompt": "¿Cuál de estos correos es legítimo?",
        "options": [
            {"id": "a", "label": "Soporte: http://seguridad-banco-login.co", "is_correct": False, "domain": "banco-login.co"},
            {"id": "b", "label": "Promos: http://free-iphone.me", "is_correct": False, "domain": "free-iphone.me"},
            {"id": "c", "label": "Banco oficial: https://banco.com/seguridad", "is_correct": True, "domain": "banco.com"}
        ],
        "hint": "Observa el dominio real del enlace."
    },
    {
        "type": "caesar",
        "title": "Cifrado César",
        "prompt": "Descifra el mensaje: Uifsf jt op tqppo",
        "cipher": "Uifsf jt op tqppo",
        "solution": "There is no spoon",
        "hint": "César sabía contar hasta 1."
    }
]


def init_session():
    """Inicializa la sesión del juego"""
    if "time_left" not in session:
        session["time_left"] = INITIAL_TIME
    if "level" not in session:
        session["level"] = 0
    if "hints_left" not in session:
        session["hints_left"] = INITIAL_HINTS
    if "status" not in session:
        session["status"] = "playing"


def validate_time():
    """Valida que el tiempo no se haya agotado"""
    if session.get("time_left", 0) <= 0:
        session["status"] = "lost"
        return False
    return True


def get_current_level():
    """Obtiene el nivel actual"""
    level_index = session.get("level", 0)
    if level_index < len(LEVELS):
        return LEVELS[level_index]
    return None


@app.route('/')
def home():
    """Página de inicio"""
    return render_template('home.html')


@app.route('/howto')
def howto():
    """Página de instrucciones"""
    return render_template('howto.html')


@app.route('/game', methods=['GET', 'POST'])
def game():
    """Pantalla principal del juego"""
    init_session()
    
    # Verificar si el juego ya terminó
    if session["status"] != "playing":
        if session["status"] == "won":
            return redirect(url_for('win'))
        elif session["status"] == "lost":
            return redirect(url_for('lose'))
    
    # Validar tiempo
    if not validate_time():
        return redirect(url_for('lose'))
    
    current_level = get_current_level()
    if not current_level:
        session["status"] = "won"
        return redirect(url_for('win'))
    
    error_message = ""
    success_message = ""
    
    if request.method == 'POST':
        # Sincronizar tiempo del cliente con el servidor
        client_time = request.form.get('time_left', type=int)
        if client_time is not None:
            session["time_left"] = min(session["time_left"], client_time)
        
        # Validar tiempo nuevamente después de sincronización
        if not validate_time():
            return redirect(url_for('lose'))
        
        # Procesar respuesta según el tipo de nivel
        if current_level["type"] == "password":
            answer = request.form.get('password', '').strip()
            if answer == current_level["solution"]:
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                success_message = "¡Contraseña correcta! +30 segundos"
            else:
                error_message = "Contraseña incorrecta. Intenta de nuevo."
        
        elif current_level["type"] == "phishing":
            answer = request.form.get('phishing_choice', '')
            correct_option = next((opt for opt in current_level["options"] if opt["is_correct"]), None)
            
            if answer == correct_option["id"]:
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                success_message = "¡Correcto! Has identificado el phishing. +30 segundos"
            else:
                error_message = "Incorrecto. Revisa los dominios de los enlaces."
        
        elif current_level["type"] == "caesar":
            answer = request.form.get('caesar_answer', '').strip()
            if answer.lower() == current_level["solution"].lower():
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                success_message = "¡Mensaje descifrado correctamente! +30 segundos"
            else:
                error_message = "Descifrado incorrecto. Intenta de nuevo."
        
        # Verificar si completó todos los niveles
        if session["level"] >= len(LEVELS):
            session["status"] = "won"
            return redirect(url_for('win'))
    
    return render_template('game.html', 
                         level=current_level, 
                         level_number=session["level"] + 1,
                         total_levels=len(LEVELS),
                         time_left=session["time_left"],
                         hints_left=session["hints_left"],
                         error_message=error_message,
                         success_message=success_message)


@app.route('/hint', methods=['POST'])
def hint():
    """Procesa la solicitud de pista"""
    init_session()
    
    if not validate_time():
        return redirect(url_for('lose'))
    
    # Sincronizar tiempo del cliente
    client_time = request.form.get('time_left', type=int)
    if client_time is not None:
        session["time_left"] = min(session["time_left"], client_time)
    
    if session["hints_left"] > 0:
        session["hints_left"] -= 1
        session["time_left"] -= HINT_PENALTY
        
        current_level = get_current_level()
        if current_level:
            return {"hint": current_level["hint"], "hints_left": session["hints_left"]}
    
    return {"hint": "No tienes más pistas disponibles.", "hints_left": session["hints_left"]}


@app.route('/reset')
def reset():
    """Reinicia el juego"""
    session.clear()
    return redirect(url_for('home'))


@app.route('/win')
def win():
    """Pantalla de victoria"""
    if session.get("status") != "won":
        return redirect(url_for('home'))
    
    final_time = session.get("time_left", 0)
    minutes = final_time // 60
    seconds = final_time % 60
    
    return render_template('win.html', 
                         final_time=final_time,
                         minutes=minutes,
                         seconds=seconds)


@app.route('/lose')
def lose():
    """Pantalla de derrota"""
    if session.get("status") != "lost":
        return redirect(url_for('home'))
    
    return render_template('lose.html')


if __name__ == '__main__':
    app.run(debug=True)
