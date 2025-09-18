"""
Escape Room de Ciberseguridad - Cyber Bomb
Aplicación principal Flask
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from utils.crypto import decrypt_caesar
import secrets
import re
import time

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
        "type": "ransomware",
        "title": "Explosión Ransomware — 'La llave perdida'",
        "prompt": "Recupera la clave de desencriptación antes de que se acabe el tiempo",
        "solution": "BLUEBELL2025",
        "hint": "PISTAS IMPORTANTES:\n1. Usa el decodificador Base64 con \"QkxVRQ==\"\n2. Resuelve el anagrama \"LEBEL\"\n3. Calcula 32 XOR 48 (no 32 elevado a 48)\n4. Los números 52, 30, 25 forman un año\n5. La clave final es: PALABRA1 + PALABRA2 + AÑO (todo junto, sin espacios)",
        "files": [
            {"name": "documento.txt.locked", "clue": "QkxVRQ== (Pista: Esto parece Base64, ¡decodifícalo!)"},
            {"name": "imagen.jpg.locked", "clue": "LEBEL (Pista: Las letras están mezcladas, ¡ordénalas!)"},
            {"name": "video.mp4.locked", "clue": "32^48 (Pista: Usa XOR, no potencia matemática)"},
            {"name": "backup.zip.locked", "clue": "52 (Pista: Parte del año final)"},
            {"name": "config.ini.locked", "clue": "30 (Pista: También parte del año)"},
            {"name": "data.db.locked", "clue": "25 (Pista: Completa el año 20_)"}
        ],
        "ransom_note": "🔒 TUS ARCHIVOS HAN SIDO ENCRIPTADOS 🔒\n\nPara recuperar tus archivos, necesitas la clave maestra.\nLas pistas están ocultas en los nombres y metadatos.\n\n💡 Pista: Los números al final no son casualidad..."
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
    if "performance_data" not in session:
        session["performance_data"] = []
    if "question_start_time" not in session:
        session["question_start_time"] = time.time()
    if "individual_times" not in session:
        session["individual_times"] = []  # Lista para almacenar tiempos individuales


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


def registrar_respuesta(pregunta_id, texto_pregunta, es_correcta, tiempo_individual=None):
    """Registra el rendimiento de una respuesta del jugador"""
    tiempo_actual = time.time()
    tiempo_respuesta = tiempo_actual - session.get("question_start_time", tiempo_actual)
    
    # Usar el tiempo individual del frontend si está disponible
    if tiempo_individual is not None:
        tiempo_respuesta = float(tiempo_individual)
    
    datos_pregunta = {
        "id_pregunta": pregunta_id,
        "texto_pregunta": texto_pregunta,
        "tiempo_respuesta": round(tiempo_respuesta, 2),
        "es_respuesta_correcta": es_correcta
    }
    
    if "performance_data" not in session:
        session["performance_data"] = []
    
    if "individual_times" not in session:
        session["individual_times"] = []
    
    session["performance_data"].append(datos_pregunta)
    
    # Registrar tiempo individual con información de la pregunta
    tiempo_info = {
        "pregunta_numero": pregunta_id,
        "titulo_pregunta": texto_pregunta,
        "tiempo_segundos": round(tiempo_respuesta, 2),
        "es_correcta": es_correcta
    }
    session["individual_times"].append(tiempo_info)
    
    session["question_start_time"] = tiempo_actual  # Reiniciar para la siguiente pregunta


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
        
        # Capturar tiempo individual de respuesta del frontend
        tiempo_individual = request.form.get('question_response_time')
        
        # Procesar respuesta según el tipo de nivel
        if current_level["type"] == "password":
            answer = request.form.get('password', '').strip()
            if answer == current_level["solution"]:
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                # Verificar si completó todos los niveles
                if session["level"] >= len(LEVELS):
                    session["status"] = "won"
                    return redirect(url_for('win'))
                # Redirigir para mostrar el siguiente nivel
                return redirect(url_for('game'))
            else:
                error_message = "Contraseña incorrecta. Intenta de nuevo."
        
        elif current_level["type"] == "phishing":
            answer = request.form.get('phishing_choice', '')
            correct_option = next((opt for opt in current_level["options"] if opt["is_correct"]), None)
            es_correcta = answer == correct_option["id"]
            registrar_respuesta(session["level"] + 1, current_level["prompt"], es_correcta, tiempo_individual)
            
            if es_correcta:
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                # Verificar si completó todos los niveles
                if session["level"] >= len(LEVELS):
                    session["status"] = "won"
                    return redirect(url_for('win'))
                # Redirigir para mostrar el siguiente nivel
                return redirect(url_for('game'))
            else:
                error_message = "Incorrecto. Revisa los dominios de los enlaces."
        
        elif current_level["type"] == "ransomware":
            answer = request.form.get('ransomware_key', '').strip().upper()
            es_correcta = answer == current_level["solution"]
            registrar_respuesta(session["level"] + 1, current_level["prompt"], es_correcta, tiempo_individual)
            
            if es_correcta:
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                # Verificar si completó todos los niveles
                if session["level"] >= len(LEVELS):
                    session["status"] = "won"
                    return redirect(url_for('win'))
                # Redirigir para mostrar el siguiente nivel
                return redirect(url_for('game'))
            else:
                error_message = "Clave de desencriptación incorrecta. Analiza las pistas más cuidadosamente."
    
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
            return jsonify({"hint": current_level["hint"], "hints_left": session["hints_left"]})
    
    return jsonify({"hint": "No tienes más pistas disponibles.", "hints_left": session["hints_left"]})


@app.route('/reset')
def reset():
    """Reinicia el juego"""
    session.clear()
    return redirect(url_for('home'))


@app.route('/win')
def win():
    """Página de victoria"""
    if session.get("status") != "won":
        return redirect(url_for('home'))
    
    # Calcular estadísticas finales
    tiempo_total = INITIAL_TIME - session.get("time_left", 0)
    performance_data = session.get("performance_data", [])
    individual_times = session.get("individual_times", [])
    
    # Calcular estadísticas de rendimiento
    total_preguntas = len(performance_data)
    respuestas_correctas = sum(1 for p in performance_data if p["es_respuesta_correcta"])
    tiempo_promedio = sum(p["tiempo_respuesta"] for p in performance_data) / total_preguntas if total_preguntas > 0 else 0
    
    # Calcular estadísticas de tiempos individuales
    tiempo_total_individual = sum(t["tiempo_segundos"] for t in individual_times)
    tiempo_promedio_individual = tiempo_total_individual / len(individual_times) if individual_times else 0
    
    stats = {
        "tiempo_total": tiempo_total,
        "total_preguntas": total_preguntas,
        "respuestas_correctas": respuestas_correctas,
        "tiempo_promedio": round(tiempo_promedio, 2),
        "performance_data": performance_data,
        "individual_times": individual_times,
        "tiempo_total_individual": round(tiempo_total_individual, 2),
        "tiempo_promedio_individual": round(tiempo_promedio_individual, 2)
    }
    
    return render_template('win.html', stats=stats)


@app.route('/lose')
def lose():
    """Pantalla de derrota"""
    if session.get("status") != "lost":
        return redirect(url_for('home'))
    
    return render_template('lose.html')


if __name__ == '__main__':
    app.run(debug=True)
