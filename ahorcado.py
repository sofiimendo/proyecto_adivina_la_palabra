import random
import unicodedata

def quitar_tildes(texto):
    """
    Convierte 'á', 'é', 'í', 'ó', 'ú', 'ñ' en 'a', 'e', 'i', 'o', 'u', 'n' para comparar.
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def obtener_palabra_secreta() -> str:
    PALABRAS = {
        "animales": ['tiburón', 'jirafa', 'elefante', 'león', 'gato', 'perro', 'cocodrilo', 'ballena', 'cebra', 'erizo'],
        "plantas": ['jazmín', 'helecho', 'ficus', 'diente de león', 'cactus', 'aloe vera', 'narcizo', 'margarita', 'rosa', 'cola de zorro'],
        "frutas_y_verduras": ['morrón', 'cebolla', 'zanahoria', 'manzana', 'pera', 'papa', 'tomate', 'frutilla', 'sandia', 'coliflor']
    }
    print("Elige una categoría para jugar: animales, plantas, frutas_y_verduras")
    categoria = input("Categoría (o ENTER para aleatoria): ").lower().strip()

    if categoria not in PALABRAS:  # si no escribe nada válido → al azar
        categoria = random.choice(list(PALABRAS.keys()))

    palabra = random.choice(PALABRAS[categoria])
    print(f"Categoría elegida: {categoria}")  # feedback al jugador
    return palabra

def elegir_dificultad() -> str:
    print("\nElegí dificultad:")
    print("  1) Fácil   (muestra 1ª y última letra)")
    print("  2) Medio   (muestra solo la última letra)")
    print("  3) Difícil (no muestra letras)")
    while True:
        op = input("Opción: ").strip()
        if op == "1":
            return "facil"
        if op == "2":
            return "medio"
        if op == "3":
            return "dificil"
        print("Opción inválida. Probá con 1, 2 o 3.")

def indices_primera_y_ultima_letra_no_espacio(palabra: str) -> tuple[int, int]:
    """Devuelve (i_primera, i_ultima) ignorando espacios en los extremos."""
    # primera no espacio
    i_prim = next((i for i, ch in enumerate(palabra) if ch != " "), 0)
    # última no espacio
    i_ult = next((i for i in range(len(palabra) - 1, -1, -1) if palabra[i] != " "), len(palabra) - 1)
    return i_prim, i_ult

def mostrar_progreso(palabra_secreta, letras_adivinadas, indices_revelados=None):
    """
    Muestra progreso: letras adivinadas (comparando sin tildes) y
    además revela siempre las posiciones en 'indices_revelados'.
    """
    if indices_revelados is None:
        indices_revelados = set()

    adivinado = ''
    for idx, letra in enumerate(palabra_secreta):
        if letra == " ":
            adivinado += " "
        elif idx in indices_revelados:
            adivinado += letra
        elif quitar_tildes(letra.lower()) in letras_adivinadas:
            adivinado += letra  # muestra la letra original con tilde si la tiene
        else:
            adivinado += "_"
    return adivinado

def juego_ahorcado():
    palabra_secreta = obtener_palabra_secreta()
    palabra_sin_tildes = quitar_tildes(palabra_secreta.lower())

    # --- elegir dificultad y preparar revelados iniciales ---
    dificultad = elegir_dificultad()
    indices_revelados = set()

    # cálculo de primera y última (ignorando espacios)
    i_prim, i_ult = indices_primera_y_ultima_letra_no_espacio(palabra_secreta)

    # conjunto de letras únicas (normalizadas) sin contar espacios
    letras_unicas_norm = {
        quitar_tildes(ch.lower()) for ch in palabra_secreta if ch != " "
    }

    # REGLAS: por posición (no destapa todas las iguales)
    if dificultad == "facil":
        if len(letras_unicas_norm) == 1:
            # todas iguales → mostrar solo una posición (la primera)
            indices_revelados.add(i_prim)
        else:
            indices_revelados.update({i_prim, i_ult})
    elif dificultad == "medio":
        # medio: solo última; si todas iguales da igual (sigue siendo una sola posición)
        indices_revelados.add(i_ult)
    # difícil: no agrega nada

    letras_adivinadas = []     # guardás letras normalizadas (sin tildes)
    letras_incorrectas = []    # solo para mostrar
    intentos = 6               # ahora 6 intentos
    juego_terminado = False

    print(f"\nTenés {intentos} intentos para adivinar la palabra secreta")
    print(mostrar_progreso(palabra_secreta, letras_adivinadas, indices_revelados),
        "La cantidad de letras de la palabra es:", len(palabra_secreta))

    while not juego_terminado and intentos > 0:
        pedir_letra = input("Introduce una letra: ").lower()
        pedir_letra_sin_tilde = quitar_tildes(pedir_letra)

        if len(pedir_letra) != 1 or not pedir_letra.isalpha():
            print("Por favor, tienes que introducir una letra válida")
            continue

        if pedir_letra_sin_tilde in letras_adivinadas:
            print("Ya has utilizado esa letra, prueba con otra")
            continue  # no resta intentos

        # registramos la letra como usada
        letras_adivinadas.append(pedir_letra_sin_tilde)

        if pedir_letra_sin_tilde in palabra_sin_tildes:
            print(f"¡Has acertado, la letra '{pedir_letra}' está presente en la palabra!")
        else:
            letras_incorrectas.append(pedir_letra)
            intentos -= 1
            print(f"Te quedan {intentos} intentos")
            print("Las letras incorrectas son: ", letras_incorrectas)

        progreso_actual = mostrar_progreso(palabra_secreta, letras_adivinadas, indices_revelados)
        print(progreso_actual)

        if "_" not in progreso_actual:
            juego_terminado = True
            print(f"¡Felicitaciones has ganado! La palabra es: '{palabra_secreta.capitalize()}'")

        if intentos == 0:
            print(f"Lo sentimos mucho se te han acabado los intentos, la palabra secreta era '{palabra_secreta.capitalize()}'")

juego_ahorcado()
