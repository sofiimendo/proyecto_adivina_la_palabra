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
        "fyv": ['morrón', 'cebolla', 'zanahoria', 'manzana', 'pera', 'papa', 'tomate', 'frutilla', 'sandia', 'coliflor']
    }
    categoria = random.choice(list(PALABRAS.keys()))
    palabra = random.choice(PALABRAS[categoria])
    return palabra

def mostrar_progreso(palabra_secreta, letras_adivinadas):
    adivinado = ''
    for letra in palabra_secreta:
        if letra == " ":
            adivinado += " "
        elif quitar_tildes(letra.lower()) in letras_adivinadas:
            adivinado += letra  # muestra la letra original con tilde si la tiene
        else:
            adivinado += "_"
    return adivinado

def juego_ahorcado():
    palabra_secreta = obtener_palabra_secreta()
    palabra_sin_tildes = quitar_tildes(palabra_secreta.lower())

    letras_adivinadas = []
    letras_incorrectas = []
    intentos = 5
    juego_terminado = False

    print(f"Tenés {intentos} intentos para adivinar la palabra secreta")
    print(mostrar_progreso(palabra_secreta, letras_adivinadas),
          "La cantidad de letras de la palabra es:", len(palabra_secreta))

    while not juego_terminado and intentos > 0:
        pedir_letra = input("Introduce una letra: ").lower()
        pedir_letra_sin_tilde = quitar_tildes(pedir_letra)

        if len(pedir_letra) != 1 or not pedir_letra.isalpha():
            print("Por favor, tienes que introducir una letra válida")
            continue

        if pedir_letra_sin_tilde in letras_adivinadas:
            print("Ya has utilizado esa letra, prueba con otra")
            continue  # 👈 para que no siga el flujo ni reste intentos

        letras_adivinadas.append(pedir_letra_sin_tilde)

        if pedir_letra_sin_tilde in palabra_sin_tildes:
            print(f"¡Has acertado, la letra '{pedir_letra}' está presente en la palabra!")
        else:
            letras_incorrectas.append(pedir_letra)
            intentos -= 1
            print(f"Te quedan {intentos} intentos")
            print("Las letras incorrectas son: ", letras_incorrectas)

        progreso_actual = mostrar_progreso(palabra_secreta, letras_adivinadas)
        print(progreso_actual)

        if "_" not in progreso_actual:
            juego_terminado = True
            print(f"¡Felicitaciones has ganado! La palabra es: '{palabra_secreta.capitalize()}'")

        if intentos == 0:
            print(f"Lo sentimos mucho se te han acabado los intentos, la palabra secreta era '{palabra_secreta.capitalize()}'")

juego_ahorcado()
