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
INITIAL_HINTS = 8  # Más pistas iniciales
TIME_BONUS = 30  # segundos por nivel completado
HINT_PENALTY = 8  # menos penalización por pista (era 10)
HINT_BONUS = 2  # pistas adicionales por nivel completado

# Definición de niveles
LEVELS = [
    {
        "type": "password",
        "title": "Contraseña Débil",
        "prompt": "Ingresa la contraseña del administrador del sistema.",
        "solution": "1234",
        "hint": "El admin nunca cambia su clave… empieza con 1.",
        "success_message": "¡Excelente! Has aprendido sobre contraseñas débiles. 💡 TIP: Las contraseñas como '1234', 'password' o 'admin' son extremadamente vulnerables. Siempre usa contraseñas complejas con mayúsculas, minúsculas, números y símbolos.",
        "additional_hints": [
            "Es una secuencia numérica muy simple",
            "Piensa en los números más básicos",
            "Es una contraseña de 4 dígitos",
            "Los administradores perezosos usan contraseñas obvias",
            "Empieza con 1 y sigue con 2, 3, 4...",
            "Es la secuencia más básica que existe",
            "Los números van en orden ascendente",
            "¡Es tan simple que un niño la adivinaría!"
        ]
    },
    {
        "type": "caesar",
        "title": "Cifrado César",
        "prompt": "Descifra el mensaje encriptado usando el cifrado César. El mensaje fue cifrado con un desplazamiento de 3 posiciones hacia adelante en el alfabeto.",
        "encrypted_message": "WKH VHFUHW SDVVZRUG LV FLEHUVHFXULGDG",
        "solution": "THE SECRET PASSWORD IS CYBERSECURITY",
        "hint": "El cifrado César desplaza cada letra 3 posiciones hacia atrás en el alfabeto. A=D, B=E, C=F, etc. Para descifrar, mueve cada letra 3 posiciones hacia atrás.",
        "success_message": "¡Fantástico! Has dominado el cifrado César. 🔐 TIP: El cifrado César es uno de los métodos más antiguos de encriptación. Aunque es fácil de romper con análisis de frecuencia, fue usado por Julio César para comunicaciones militares. Los métodos modernos como AES son mucho más seguros.",
        "additional_hints": [
            "Usa la herramienta de descifrado con desplazamiento 3",
            "El mensaje contiene la palabra 'SECRET'",
            "La respuesta final es sobre ciberseguridad",
            "Cada letra se mueve 3 posiciones hacia atrás en el alfabeto",
            "W se convierte en T, K se convierte en H, H se convierte en E",
            "El mensaje descifrado habla de una contraseña secreta",
            "La palabra final es 'CYBERSECURITY'",
            "Usa el botón 'Descifrar' en la herramienta",
            "El resultado debe ser: THE SECRET PASSWORD IS CYBERSECURITY"
        ]
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
        "hint": "Observa el dominio real del enlace.",
        "success_message": "¡Perfecto! Has identificado correctamente el correo legítimo. 🛡️ TIP: Los ataques de phishing son muy comunes. Siempre verifica la URL completa, busca certificados SSL válidos, y nunca hagas clic en enlaces sospechosos. Los bancos nunca te pedirán datos por email.",
        "additional_hints": [
            "Los dominios legítimos suelen ser simples y reconocibles",
            "Evita dominios con guiones o extensiones extrañas",
            "El banco oficial tendría un dominio .com limpio",
            "Los atacantes usan dominios similares pero no idénticos",
            "banco-login.co tiene un guión sospechoso",
            "free-iphone.me suena demasiado bueno para ser verdad",
            "banco.com es el dominio más limpio y profesional",
            "Los bancos reales usan dominios cortos y memorables",
            "La opción C es la única con HTTPS y dominio limpio",
            "Los phishers copian nombres pero cambian extensiones"
        ]
    },
    {
        "type": "ransomware",
        "title": "Explosión Ransomware — 'La llave perdida'",
        "prompt": "Recupera la clave de desencriptación antes de que se acabe el tiempo",
        "solution": "BLUEBELL2025",
        "hint": "PISTAS IMPORTANTES:\n1. Usa el decodificador Base64 con \"QkxVRQ==\"\n2. Resuelve el anagrama \"LEBEL\"\n3. Calcula 32 XOR 48 (no 32 elevado a 48)\n4. Los números 52, 30, 25 forman un año\n5. La clave final es: PALABRA1 + PALABRA2 + AÑO (todo junto, sin espacios)",
        "success_message": "¡Increíble! Has resuelto el ransomware y recuperado los archivos. 🎉 TIP: Los ransomware son una amenaza real. Siempre mantén copias de seguridad actualizadas, no abras archivos sospechosos, y mantén tu software actualizado. La prevención es la mejor defensa contra estos ataques.",
        "additional_hints": [
            "Base64 'QkxVRQ==' se decodifica como 'BLUE'",
            "LEBEL es un anagrama de 'BELL'",
            "32 XOR 48 = 16 (usa la operación XOR)",
            "Los números 52, 30, 25 forman el año 2025",
            "Combina: BLUE + BELL + 2025 = BLUEBELL2025",
            "Usa la herramienta Base64 Decoder con QkxVRQ==",
            "Resuelve el anagrama LEBEL para obtener BELL",
            "Calcula 32 XOR 48 usando la herramienta XOR Calculator",
            "Los números 52, 30, 25 forman 2025 (año actual)",
            "La clave final es BLUEBELL2025 (todo junto)",
            "No uses espacios en la respuesta final",
            "La clave tiene 13 caracteres en total"
        ],
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
    if "hint_count" not in session:
        session["hint_count"] = 0  # Contador de pistas usadas en el nivel actual


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
                # Guardar mensaje de éxito
                session["success_message"] = current_level.get("success_message", "¡Excelente! Has completado el nivel.")
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                session["hints_left"] += HINT_BONUS  # Otorgar pistas adicionales
                session["hint_count"] = 0  # Reiniciar contador de pistas para el nuevo nivel
                # Verificar si completó todos los niveles
                if session["level"] >= len(LEVELS):
                    session["status"] = "won"
                    return redirect(url_for('win'))
                # Redirigir para mostrar el siguiente nivel
                return redirect(url_for('game'))
            else:
                error_message = "Contraseña incorrecta. Intenta de nuevo."
        
        elif current_level["type"] == "caesar":
            answer = request.form.get('caesar_answer', '').strip().upper()
            es_correcta = answer == current_level["solution"]
            registrar_respuesta(session["level"] + 1, current_level["prompt"], es_correcta, tiempo_individual)
            
            if es_correcta:
                # Guardar mensaje de éxito
                session["success_message"] = current_level.get("success_message", "¡Excelente! Has completado el nivel.")
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                session["hints_left"] += HINT_BONUS  # Otorgar pistas adicionales
                session["hint_count"] = 0  # Reiniciar contador de pistas para el nuevo nivel
                # Verificar si completó todos los niveles
                if session["level"] >= len(LEVELS):
                    session["status"] = "won"
                    return redirect(url_for('win'))
                # Redirigir para mostrar el siguiente nivel
                return redirect(url_for('game'))
            else:
                error_message = "Mensaje descifrado incorrecto. Revisa tu cifrado César."
        
        elif current_level["type"] == "phishing":
            answer = request.form.get('phishing_choice', '')
            correct_option = next((opt for opt in current_level["options"] if opt["is_correct"]), None)
            es_correcta = answer == correct_option["id"]
            registrar_respuesta(session["level"] + 1, current_level["prompt"], es_correcta, tiempo_individual)
            
            if es_correcta:
                # Guardar mensaje de éxito
                session["success_message"] = current_level.get("success_message", "¡Excelente! Has completado el nivel.")
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                session["hints_left"] += HINT_BONUS  # Otorgar pistas adicionales
                session["hint_count"] = 0  # Reiniciar contador de pistas para el nuevo nivel
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
                # Guardar mensaje de éxito
                session["success_message"] = current_level.get("success_message", "¡Excelente! Has completado el nivel.")
                session["level"] += 1
                session["time_left"] += TIME_BONUS
                session["hints_left"] += HINT_BONUS  # Otorgar pistas adicionales
                session["hint_count"] = 0  # Reiniciar contador de pistas para el nuevo nivel
                # Verificar si completó todos los niveles
                if session["level"] >= len(LEVELS):
                    session["status"] = "won"
                    return redirect(url_for('win'))
                # Redirigir para mostrar el siguiente nivel
                return redirect(url_for('game'))
            else:
                error_message = "Clave de desencriptación incorrecta. Analiza las pistas más cuidadosamente."
    
    # Obtener mensaje de éxito de la sesión si existe
    session_success_message = session.pop("success_message", None)
    if session_success_message:
        success_message = session_success_message
    
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
            # Sistema de pistas progresivas
            hint_count = session.get("hint_count", 0)
            hint_count += 1
            session["hint_count"] = hint_count
            
            # Primera pista: pista principal
            if hint_count == 1:
                hint_text = current_level["hint"]
            # Pistas adicionales si están disponibles
            elif "additional_hints" in current_level and hint_count <= len(current_level["additional_hints"]) + 1:
                hint_text = current_level["additional_hints"][hint_count - 2]
            else:
                hint_text = "No hay más pistas específicas para este nivel. ¡Usa tu ingenio!"
            
            return jsonify({
                "hint": hint_text, 
                "hints_left": session["hints_left"],
                "hint_number": hint_count,
                "total_hints": len(current_level.get("additional_hints", [])) + 1
            })
    
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
    app.run(debug=True, port=5001)
