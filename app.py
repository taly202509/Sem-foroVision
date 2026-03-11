# ============================================================
#  SemáforoVision — Detector de semáforo para monocromatismo
#  Proyecto TIC · Ingeniería de Sistemas · Primer Semestre
# ============================================================

import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="SemáforoVision", page_icon="🚦")

# ── Diccionario con los mensajes de cada color ──────────────
mensajes = {
    "ROJO":        "🔴 LUZ ROJA — DETENTE. No puedes cruzar.",
    "AMARILLO":    "🟡 LUZ AMARILLA — PRECAUCIÓN. Prepárate para detenerte.",
    "VERDE":       "🟢 LUZ VERDE — PUEDES PASAR. Cruza con cuidado.",
    "DESCONOCIDO": "⚪ No se identificó el color del semáforo. Asegúrate de que el semáforo esté centrado en la cámara.",
}


# ── Función 1: Recortar la zona central de la imagen ────────
def recortar_zona_central(imagen):
    alto  = imagen.shape[0]
    ancho = imagen.shape[1]

    x1 = int(ancho * 0.40)
    x2 = int(ancho * 0.60)
    y1 = int(alto  * 0.20)
    y2 = int(alto  * 0.80)

    zona = imagen[y1:y2, x1:x2]

    return zona, x1, y1, x2, y2


# ── Función 2: Contar píxeles de cada color ─────────────────
def contar_pixeles_por_color(zona_bgr):
    zona_hsv = cv2.cvtColor(zona_bgr, cv2.COLOR_BGR2HSV)

    minimo_rojo_1   = np.array([0,   120, 100])
    maximo_rojo_1   = np.array([10,  255, 255])
    minimo_rojo_2   = np.array([160, 120, 100])
    maximo_rojo_2   = np.array([180, 255, 255])
    minimo_amarillo = np.array([18,  100, 100])
    maximo_amarillo = np.array([35,  255, 255])
    minimo_verde    = np.array([40,  80,  80])
    maximo_verde    = np.array([90,  255, 255])

    mascara_rojo_1   = cv2.inRange(zona_hsv, minimo_rojo_1,   maximo_rojo_1)
    mascara_rojo_2   = cv2.inRange(zona_hsv, minimo_rojo_2,   maximo_rojo_2)
    mascara_amarillo = cv2.inRange(zona_hsv, minimo_amarillo, maximo_amarillo)
    mascara_verde    = cv2.inRange(zona_hsv, minimo_verde,    maximo_verde)

    mascara_rojo = cv2.bitwise_or(mascara_rojo_1, mascara_rojo_2)

    pixeles_rojo     = int(np.sum(mascara_rojo     > 0))
    pixeles_amarillo = int(np.sum(mascara_amarillo > 0))
    pixeles_verde    = int(np.sum(mascara_verde    > 0))

    return pixeles_rojo, pixeles_amarillo, pixeles_verde


# ── Función 3: Decidir cuál color es el dominante ───────────
def detectar_color_semaforo(pixeles_rojo, pixeles_amarillo, pixeles_verde):
    MINIMO_PIXELES  = 150
    color_detectado = "DESCONOCIDO"

    if pixeles_rojo >= MINIMO_PIXELES or pixeles_amarillo >= MINIMO_PIXELES or pixeles_verde >= MINIMO_PIXELES:
        if pixeles_rojo >= pixeles_amarillo and pixeles_rojo >= pixeles_verde:
            color_detectado = "ROJO"
        elif pixeles_amarillo >= pixeles_rojo and pixeles_amarillo >= pixeles_verde:
            color_detectado = "AMARILLO"
        else:
            color_detectado = "VERDE"

    return color_detectado


# ── Función 4: Dibujar el recuadro de análisis ──────────────
def dibujar_zona(imagen_bgr, x1, y1, x2, y2):
    imagen_con_zona = imagen_bgr.copy()
    cv2.rectangle(imagen_con_zona, (x1, y1), (x2, y2), (124, 106, 255), 3)
    return imagen_con_zona


# ══════════════════════════════════════════════════════════════
#  INTERFAZ PRINCIPAL
# ══════════════════════════════════════════════════════════════

st.title("🚦 SemáforoVision")
st.write("Herramienta para personas con monocromatismo (daltonismo total)")
st.write("Apunta la cámara al semáforo y toma la foto.")

foto = st.camera_input("Tomar foto")

if foto is not None:

    imagen_pil = Image.open(foto)
    imagen_np  = np.array(imagen_pil)
    imagen_bgr = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2BGR)

    zona, x1, y1, x2, y2                         = recortar_zona_central(imagen_bgr)
    pixeles_rojo, pixeles_amarillo, pixeles_verde = contar_pixeles_por_color(zona)
    color                                         = detectar_color_semaforo(pixeles_rojo, pixeles_amarillo, pixeles_verde)

    imagen_marcada = dibujar_zona(imagen_bgr, x1, y1, x2, y2)
    imagen_rgb     = cv2.cvtColor(imagen_marcada, cv2.COLOR_BGR2RGB)

    st.image(imagen_rgb, caption="Zona analizada", use_container_width=True)

    st.subheader("Resultado:")
    st.title(mensajes[color])

    st.write("Píxeles detectados:")
    st.write("Rojo:     " + str(pixeles_rojo))
    st.write("Amarillo: " + str(pixeles_amarillo))

    st.write("Verde:    " + str(pixeles_verde))

