# 🎮 Proyecto: Adivina la Palabra (Ahorcado)

Este proyecto fue realizado en equipo como parte del curso **Introducción a Python** en **ADA**.
El objetivo es poner en práctica los primeros conceptos aprendidos de programación, trabajando en lógica, estructuras de control y manejo de cadenas.

---

## 👩‍💻 Participantes
- Yamila Valdez Aguilar
- Thelma D Teileche
- Sofía Macarena Mendoza

---

## 📌 Descripción del Juego
**Adivina la Palabra (Ahorcado)** es una versión del clásico juego de adivinanza:

- El programa selecciona una palabra secreta de manera aleatoria.
- El jugador debe adivinarla ingresando letras.
- Si la letra está en la palabra, se muestra en la posición correspondiente.
- Si no está, se descuenta un intento.
- El juego termina cuando se completa la palabra o se agotan los intentos.

### Funcionalidades extra:
✅ No se descuentan intentos si se repite una letra ya utilizada.
✅ Manejo de palabras con tildes (ejemplo: “camión” = “camion”).
✅ Versión gráfica con **Flet** que usa imágenes y sonidos para mejorar la experiencia.

---

## 🚀 Tecnologías utilizadas
- **Python 3.x**
- Librerías estándar:
  - `random`
  - `unicodedata`
  - `os`
- **Flet** (para la versión gráfica)

---

## 📂 Estructura del proyecto

proyecto_adivina_la_palabra/
│
├── ahorcado.py # Juego principal en consola
├── ahorcado_flet.py # Juego con interfaz gráfica usando Flet
├── README.md # Documentación del proyecto
├── assets/ # Carpeta con imágenes y sonidos
│ ├── images/
│ │ ├── letters/ # Letras en imágenes (a.png, b.png, ...)
│ │ └── hangman/ # Etapas del ahorcado (stage-0.png ... stage-7.png)
│ └── sounds/ # Sonidos (correct.mp3, wrong.mp3, lose.mp3)
└── .github/
└── PULL_REQUEST_TEMPLATE.md # Plantilla de Pull Requests

---

## 🕹️ Cómo ejecutar el proyecto

### ▶️ Versión en consola

python ahorcado.py

🖥️ Versión con interfaz gráfica (Flet)

1- Instalar dependencias (si no las tenés):

    pip install flet flet-audio

2- Ejecutar el juego:

    python ahorcado_flet.py


## 📖 Aprendizajes

- Trabajo en equipo y uso de GitHub.

- Primeros pasos en Python con condicionales, bucles, funciones y manejo de cadenas.

- Integración de imágenes con la librería Flet.

- Manejo de errores y casos especiales en un programa interactivo.

## 📜 Licencia
- Este proyecto se comparte con fines educativos.
- Puedes usarlo y modificarlo libremente.