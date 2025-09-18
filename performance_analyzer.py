#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador de Rendimiento del Juego de Ciberseguridad
Genera reportes detallados del rendimiento de los jugadores
"""

def analizar_rendimiento(datos_jugador):
    """
    Analiza los datos de rendimiento de un jugador y genera un reporte detallado.
    
    Args:
        datos_jugador (list): Lista de diccionarios con los datos de cada pregunta
                             Cada diccionario debe contener:
                             - id_pregunta: identificador único
                             - texto_pregunta: texto de la pregunta
                             - tiempo_respuesta: tiempo en segundos
                             - es_respuesta_correcta: boolean
    
    Returns:
        str: Reporte formateado del rendimiento del jugador
    """
    
    if not datos_jugador:
        return "Error: No se proporcionaron datos para analizar."
    
    # Calcular métricas básicas
    tiempo_total = sum(pregunta['tiempo_respuesta'] for pregunta in datos_jugador)
    total_preguntas = len(datos_jugador)
    respuestas_correctas = sum(1 for pregunta in datos_jugador if pregunta['es_respuesta_correcta'])
    respuestas_incorrectas = total_preguntas - respuestas_correctas
    tiempo_promedio = tiempo_total / total_preguntas if total_preguntas > 0 else 0
    
    # Encontrar preguntas con tiempos extremos
    pregunta_mas_rapida = min(datos_jugador, key=lambda x: x['tiempo_respuesta'])
    pregunta_mas_lenta = max(datos_jugador, key=lambda x: x['tiempo_respuesta'])
    
    # Generar reporte
    reporte = f"""
=== REPORTE DE RENDIMIENTO DEL JUGADOR ===

Tiempo total de juego: {tiempo_total:.2f} segundos.

Preguntas respondidas: {total_preguntas}

Respuestas correctas: {respuestas_correctas}

Respuestas incorrectas: {respuestas_incorrectas}

Tiempo promedio por pregunta: {tiempo_promedio:.2f} segundos.

Pregunta respondida más rápido:
Pregunta: {pregunta_mas_rapida['texto_pregunta']}
Tiempo: {pregunta_mas_rapida['tiempo_respuesta']:.2f} segundos.

Pregunta respondida más lento:
Pregunta: {pregunta_mas_lenta['texto_pregunta']}
Tiempo: {pregunta_mas_lenta['tiempo_respuesta']:.2f} segundos.

=== ANÁLISIS ADICIONAL ===

Porcentaje de aciertos: {(respuestas_correctas/total_preguntas)*100:.1f}%
Eficiencia (aciertos/tiempo): {respuestas_correctas/tiempo_total:.3f} respuestas correctas por segundo
"""
    
    return reporte

def generar_reporte_json(datos_jugador):
    """
    Genera un reporte en formato JSON para integración con APIs.
    
    Args:
        datos_jugador (list): Lista de diccionarios con los datos de cada pregunta
    
    Returns:
        dict: Diccionario con las métricas calculadas
    """
    
    if not datos_jugador:
        return {"error": "No se proporcionaron datos para analizar"}
    
    tiempo_total = sum(pregunta['tiempo_respuesta'] for pregunta in datos_jugador)
    total_preguntas = len(datos_jugador)
    respuestas_correctas = sum(1 for pregunta in datos_jugador if pregunta['es_respuesta_correcta'])
    respuestas_incorrectas = total_preguntas - respuestas_correctas
    tiempo_promedio = tiempo_total / total_preguntas if total_preguntas > 0 else 0
    
    pregunta_mas_rapida = min(datos_jugador, key=lambda x: x['tiempo_respuesta'])
    pregunta_mas_lenta = max(datos_jugador, key=lambda x: x['tiempo_respuesta'])
    
    return {
        "tiempo_total": round(tiempo_total, 2),
        "total_preguntas": total_preguntas,
        "respuestas_correctas": respuestas_correctas,
        "respuestas_incorrectas": respuestas_incorrectas,
        "tiempo_promedio": round(tiempo_promedio, 2),
        "porcentaje_aciertos": round((respuestas_correctas/total_preguntas)*100, 1),
        "eficiencia": round(respuestas_correctas/tiempo_total, 3),
        "pregunta_mas_rapida": {
            "id": pregunta_mas_rapida['id_pregunta'],
            "texto": pregunta_mas_rapida['texto_pregunta'],
            "tiempo": pregunta_mas_rapida['tiempo_respuesta']
        },
        "pregunta_mas_lenta": {
            "id": pregunta_mas_lenta['id_pregunta'],
            "texto": pregunta_mas_lenta['texto_pregunta'],
            "tiempo": pregunta_mas_lenta['tiempo_respuesta']
        }
    }

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo para demostración
    datos_ejemplo = [
        {
            "id_pregunta": 1,
            "texto_pregunta": "¿Cuál es el protocolo más seguro para transferir archivos?",
            "tiempo_respuesta": 15.5,
            "es_respuesta_correcta": True
        },
        {
            "id_pregunta": 2,
            "texto_pregunta": "¿Qué significa SSL?",
            "tiempo_respuesta": 8.2,
            "es_respuesta_correcta": True
        },
        {
            "id_pregunta": 3,
            "texto_pregunta": "¿Cuál es el puerto por defecto de HTTPS?",
            "tiempo_respuesta": 25.7,
            "es_respuesta_correcta": False
        },
        {
            "id_pregunta": 4,
            "texto_pregunta": "¿Qué es un firewall?",
            "tiempo_respuesta": 12.3,
            "es_respuesta_correcta": True
        },
        {
            "id_pregunta": 5,
            "texto_pregunta": "¿Cuál es la diferencia entre HTTP y HTTPS?",
            "tiempo_respuesta": 18.9,
            "es_respuesta_correcta": True
        }
    ]
    
    print("=== DEMO DEL ANALIZADOR DE RENDIMIENTO ===")
    print(analizar_rendimiento(datos_ejemplo))
    
    print("\n=== REPORTE EN FORMATO JSON ===")
    import json
    reporte_json = generar_reporte_json(datos_ejemplo)
    print(json.dumps(reporte_json, indent=2, ensure_ascii=False))