# Escape Room de Ciberseguridad - Cyber Bomb

Un juego educativo de escape room que enseña conceptos básicos de ciberseguridad a través de desafíos interactivos.

## 🎯 Objetivo

Desactivar la "bomba digital" resolviendo 3 niveles de ciberseguridad antes de que se agote el tiempo. Cada nivel enseña un concepto diferente:

1. **Contraseñas Débiles**: Identificar contraseñas inseguras
2. **Phishing**: Detectar correos fraudulentos
3. **Cifrado César**: Descifrar mensajes codificados

## 🚀 Instalación

### Requisitos
- Python 3.11 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd cyber_bomb
   ```

2. **Crear entorno virtual**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Windows
   set FLASK_APP=app.py
   set FLASK_ENV=development
   
   # macOS/Linux
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

5. **Ejecutar la aplicación**
   ```bash
   flask run
   ```

6. **Abrir en el navegador**
   ```
   http://localhost:5000
   ```

## 🎮 Cómo jugar

### Mecánicas principales
- **Tiempo inicial**: 10 minutos (600 segundos)
- **Niveles**: 3 niveles secuenciales
- **Pistas**: 3 pistas disponibles (cada una resta 10 segundos)
- **Bonificación**: +30 segundos por nivel completado

### Niveles

#### Nivel 1: Contraseña Débil
- **Objetivo**: Ingresar la contraseña del administrador
- **Solución**: `1234`
- **Concepto**: Las contraseñas débiles son fáciles de adivinar

#### Nivel 2: Caza-Phish
- **Objetivo**: Identificar el correo legítimo entre 3 opciones
- **Concepto**: Verificar dominios y URLs sospechosas
- **Pista**: Observa el dominio real del enlace

#### Nivel 3: Cifrado César
- **Objetivo**: Descifrar el mensaje codificado
- **Mensaje**: `Uifsf jt op tqppo`
- **Solución**: `There is no spoon`
- **Concepto**: Cifrado por desplazamiento de caracteres

### Estrategias
- Usa las pistas estratégicamente cuando estés atascado
- Cada nivel completado te da tiempo extra
- Mantén un ojo en el cronómetro
- Lee cuidadosamente las instrucciones de cada nivel

## 🔧 Personalización

### Modificar tiempos
En `app.py`, línea ~20:
```python
session["time_left"] = 600  # Cambiar a segundos deseados
```

### Modificar pistas
En `app.py`, línea ~22:
```python
session["hints_left"] = 3  # Cambiar número de pistas
```

### Agregar nuevos niveles
En `app.py`, agregar al array `LEVELS`:
```python
{
    "type": "nuevo_tipo",
    "title": "Título del Nivel",
    "prompt": "Descripción del desafío",
    "solution": "respuesta_correcta",
    "hint": "Pista para el nivel"
}
```

## 📚 Conceptos Educativos

### Contraseñas Seguras
- Usar combinaciones de letras, números y símbolos
- Evitar información personal (fechas, nombres)
- Usar contraseñas únicas para cada servicio
- Considerar gestores de contraseñas

### Detección de Phishing
- Verificar el dominio del remitente
- Buscar errores gramaticales
- No hacer clic en enlaces sospechosos
- Verificar la legitimidad del correo

### Cifrado Básico
- El cifrado César es un método histórico simple
- Los métodos modernos son mucho más complejos
- La criptografía es fundamental en la seguridad digital

## 🛠️ Tecnologías

- **Backend**: Python 3.11+ con Flask
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Estado**: Flask sessions (sin base de datos)
- **Estilo**: Diseño minimalista con alto contraste

## 📁 Estructura del Proyecto

```
cyber_bomb/
├── app.py              # Aplicación principal Flask
├── requirements.txt    # Dependencias Python
├── README.md          # Este archivo
├── templates/         # Plantillas HTML
│   ├── base.html      # Layout base
│   ├── home.html      # Página de inicio
│   ├── howto.html     # Instrucciones
│   ├── game.html      # Pantalla de juego
│   ├── win.html       # Pantalla de victoria
│   └── lose.html      # Pantalla de derrota
└── utils/
    └── crypto.py      # Utilidades de cifrado
```

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
- Asegúrate de que el entorno virtual esté activado
- Ejecuta `pip install -r requirements.txt`

### Error: "Address already in use"
- Cambia el puerto: `flask run --port=5001`
- O termina el proceso que usa el puerto 5000

### El cronómetro no funciona
- Verifica que JavaScript esté habilitado
- Revisa la consola del navegador para errores

## 📝 Notas de Desarrollo

- El juego usa sesiones de Flask para mantener el estado
- No se requiere base de datos externa
- Diseño accesible con navegación por teclado
- Código comentado para facilitar modificaciones

## 🎓 Uso Educativo

Este proyecto es ideal para:
- Introducir conceptos de ciberseguridad
- Enseñar programación web básica
- Demostrar el uso de Flask y sesiones
- Practicar desarrollo frontend minimalista

---

**Desarrollado para fines educativos** | **Versión 1.0**
