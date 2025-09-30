import random
import unicodedata

print(f"\n 🤩 Bienvenido al juego de adivinar la palabra secreta 🤩\n")

# --- NUEVO: Selección de categoría ---
def seleccionar_categoria():
    categorias = {"1": "animales", "2": "plantas", "3": "fyv"}
    print("Selecciona la categoría:")
    print("1 - Animales")
    print("2 - Plantas")
    print("3 - Frutas y Verduras")
    opcion = ""
    while opcion not in categorias:
        opcion = input("👉 Ingresa el número de la categoría: ")
    return categorias[opcion]

# --- NUEVO: Selección de dificultad ---
def seleccionar_dificultad():
    dificultades = {"1": "facil", "2": "medio", "3": "dificil"}
    print("\nSelecciona la dificultad:")
    print("1 - Fácil (se muestran 2 letras)")
    print("2 - Medio (se muestra 1 letra)")
    print("3 - Difícil (no se muestra ninguna letra)")
    opcion = ""
    while opcion not in dificultades:
        opcion = input("👉 Ingresa el número de la dificultad: ")
    return dificultades[opcion]

#FUNCION PARA SACAR LAS TILDES
def quitar_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

#FUNCION PARA QUE SE ELIJA LA PALABRA
def obtener_palabra_secreta(categoria) -> str:
    PALABRAS = {
        "animales": ['tiburón', 'jirafa', 'elefante', 'león', 'gato', 'perro', 'cocodrilo', 'ballena', 'cebra', 'erizo'],
        "plantas": ['jazmín', 'helecho', 'ficus', 'diente de león', 'cactus', 'aloe vera', 'narcizo', 'margarita', 'rosa', 'cola de zorro'],
        "fyv": ['morrón', 'cebolla', 'zanahoria', 'manzana', 'pera', 'papa', 'tomate', 'frutilla', 'sandia', 'coliflor']
    }
    palabra = random.choice(PALABRAS[categoria])
    return palabra

#FUNCION PARA EL PROGRESO DEL JUEGO
def mostrar_progreso(palabra_secreta, letras_adivinadas):
    adivinado = ''
    for letra in palabra_secreta:
        if letra == " ":
            adivinado += " "
        elif quitar_tildes(letra.lower()) in letras_adivinadas:
            adivinado += letra  # muestra la letra original con tilde
        else:
            adivinado += "_"
    return adivinado

#LOGICA DEL JUEGO
def juego_ahorcado():
    # --- NUEVO: pedir categoría y dificultad ---
    categoria_elegida = seleccionar_categoria()
    dificultad = seleccionar_dificultad()

    palabra_secreta = obtener_palabra_secreta(categoria_elegida)
    palabra_sin_tildes = quitar_tildes(palabra_secreta.lower())

    letras_adivinadas = []
    letras_incorrectas = []
    intentos = 5
    juego_terminado = False

    # --- NUEVO: revelar letras según dificultad ---
    if dificultad == "facil":
        letras_revelar = 2
    elif dificultad == "medio":
        letras_revelar = 1
    else:
        letras_revelar = 0

    # Revelar letras automáticamente
    if letras_revelar > 0:
        letras_unicas = list(set(palabra_sin_tildes.replace(" ", "")))
        random.shuffle(letras_unicas)
        for l in letras_unicas[:letras_revelar]:
            letras_adivinadas.append(l)

    print(f"\nHas elegido la categoría: {categoria_elegida.capitalize()} | Dificultad: {dificultad.capitalize()}")
    print(f"Tenés {intentos} intentos para adivinar la palabra secreta 🔍\n")
    print(f"{mostrar_progreso(palabra_secreta, letras_adivinadas)} 🧐 La cantidad de letras de la palabra es: {len(palabra_secreta)}\n")

    while not juego_terminado and intentos > 0:
        pedir_letra = input("✨ Introduce una letra: ").lower()
        pedir_letra_sin_tilde = quitar_tildes(pedir_letra)

        if len(pedir_letra) != 1 or not pedir_letra.isalpha():
            print("⚠️ Por favor, tienes que introducir una letra válida")
            continue

        if pedir_letra_sin_tilde in letras_adivinadas:
            print("📛 Ya has utilizado esa letra, prueba con otra")
            continue  # no resta intentos

        letras_adivinadas.append(pedir_letra_sin_tilde)

        if pedir_letra_sin_tilde in palabra_sin_tildes:
            print(f"✅¡Has acertado, la letra '{pedir_letra}' está presente en la palabra!")
        else:
            letras_incorrectas.append(pedir_letra)
            intentos -= 1
            print(f"Te quedan {intentos} intentos")
            print("❌Las letras incorrectas son: ", letras_incorrectas)

        progreso_actual = mostrar_progreso(palabra_secreta, letras_adivinadas)
        print(progreso_actual)

        if "_" not in progreso_actual:
            juego_terminado = True
            print(f"🎉¡Felicitaciones has ganado! La palabra es: '{palabra_secreta.capitalize()}'")

        if intentos == 0:
            print(f"😵Lo sentimos mucho se te han acabado los intentos, la palabra secreta era '{palabra_secreta.capitalize()}'")

juego_ahorcado()


