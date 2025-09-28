import random

def obtener_palabra_secreta() -> str:

    PALABRAS = {
        "animales": ['tiburón', 'jirafa', 'elefante', 'león', 'gato', 'perro', 'cocodrilo', 'ballena', 'cebra', 'erizo'],
        "plantas": ['jazmín', 'helecho', 'ficus', 'diente de león', 'cactus', 'aloe vera', 'narcizo', 'margarita', 'rosa', 'cola de zorro'],
        "fyv": ['morrón', 'cebolla', 'zanahoria', 'manzana', 'pera', 'papa', 'tomate', 'frutilla', 'sandia', 'coliflor']
    }

    # Elegir una categoría al azar
    categoria = random.choice(list(PALABRAS.keys()))
    # Elegir una palabra dentro de esa categoría
    palabra = random.choice(PALABRAS[categoria])
    return palabra

def mostrar_progreso(palabra_secreta, letras_adivinadas):
    adivinado = ''
    for letra in palabra_secreta:
        if letra == " ":
            adivinado += " "         # para mostrar el espacio
        elif letra in letras_adivinadas:
            adivinado += letra
        else:
            adivinado += "_"
    return adivinado


def juego_ahorcado():
    palabra_secreta = obtener_palabra_secreta()
    letras_adivinadas = []
    letras_incorrectas = []
    intentos = 5
    juego_terminado = False

    print(f"Tenés {intentos} intentos para adivinar la palabra secreta")
    print(mostrar_progreso(palabra_secreta, letras_adivinadas), "La cantidad de letras de la palabra es:", len(palabra_secreta))


    while not juego_terminado and intentos > 0:
        pedir_letra = input("Introduce una letra: ").lower()

        if len(pedir_letra) != 1 or not pedir_letra.isalpha(): #usamos este metodo para que valide letras, no simbolos ni números.
            print("Por favor, tienes que introducir una letra válida")
        elif pedir_letra in letras_adivinadas:
            print("Ya has utilizado esa letra, prueba con otra")
        else:
            letras_adivinadas.append(pedir_letra)

        if pedir_letra in palabra_secreta:
                print(f"¡Has acertado, la letra '{pedir_letra}' está presente en la palabra")

        elif pedir_letra not in palabra_secreta:
            letras_incorrectas.append(pedir_letra)  # guardo la letra fallada
            intentos -= 1
            print(f"Te quedan {intentos} intentos")
            print("Las letras incorrectas son: ", letras_incorrectas)


        progreso_actual = mostrar_progreso(palabra_secreta, letras_adivinadas)
        print(progreso_actual)

        if "_" not in progreso_actual:
            juego_terminado = True
            palabra_secreta = palabra_secreta.capitalize()
            print(f"¡Felicitaciones has ganado! La palabra es: '{palabra_secreta}'")

        if intentos == 0:
            palabra_secreta = palabra_secreta.capitalize()
        print(f"Lo sentimos mucho se te han acabado los intentos, la palabra secreta era '{palabra_secreta}'")

juego_ahorcado()
