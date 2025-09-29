import flet as ft
import flet.canvas as cv
import os, random, unicodedata

# ====== Rutas ======
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR    = os.path.join(ASSETS_DIR, "images")
LETTER_DIR = os.path.join(IMG_DIR, "letters")
HANG_DIR   = os.path.join(IMG_DIR, "hangman")  # stage-01.png (pizarrón); teacher.png (opcional)

# ====== Utils ======
def quitar_tildes(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def rel_path(abs_p: str) -> str:
    return abs_p.replace(ASSETS_DIR + os.sep, "").replace("\\", "/")

def list_images(folder):
    if not os.path.isdir(folder):
        return []
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    return [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in exts]

def find_letter_asset(letter: str):
    """Busca a.png...z.png; si no, toma el primero que empiece con esa letra."""
    if not os.path.isdir(LETTER_DIR):
        return None
    l = quitar_tildes(letter.lower())[:1]
    if not l or not l.isalpha():
        return None
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        cand = os.path.join(LETTER_DIR, f"{l}{ext}")
        if os.path.exists(cand):
            return rel_path(cand)
    for f in sorted(list_images(LETTER_DIR)):
        if f.lower().startswith(l):
            return rel_path(os.path.join(LETTER_DIR, f))
    return None

def find_asset_in(folder, names):
    for f in list_images(folder):
        low = f.lower()
        if any(n in low for n in names):
            return rel_path(os.path.join(folder, f))
    return None

def find_asset_anywhere(names):
    for root, _, files in os.walk(ASSETS_DIR):
        for f in files:
            name = f.lower()
            if os.path.splitext(name)[1] not in [".png", ".jpg", ".jpeg", ".webp"]:
                continue
            if any(n in name for n in names):
                return rel_path(os.path.join(root, f))
    return None

# ====== Palabras ======
PALABRAS = {
    "animales": ['tiburón','jirafa','elefante','león','gato','perro','cocodrilo','ballena','cebra','erizo'],
    "plantas": ['jazmín','helecho','ficus','diente de león','cactus','aloe vera','narcizo','margarita','rosa','cola de zorro'],
    "frutas y verduras": ['morrón','cebolla','zanahoria','manzana','pera','papa','tomate','frutilla','sandia','coliflor'],
}

def elegir_palabra(categoria: str) -> str:
    if categoria == "aleatoria":
        categoria = random.choice(list(PALABRAS.keys()))
    return random.choice(PALABRAS[categoria])

# ====== App ======
def main(page: ft.Page):
    page.title = "Ahorcado - Flet"
    page.bgcolor = "#0d0d0d"
    page.window_min_width = 980
    page.window_min_height = 720

    # --- Activos ---
    board_src = find_asset_in(HANG_DIR, ["stage-01", "pizarron", "board"]) or \
                find_asset_anywhere(["stage-01", "pizarron", "board"])
    teacher_src = find_asset_in(HANG_DIR, ["teacher", "maestra"]) or \
                    find_asset_anywhere(["teacher", "maestra"])

    # Pizarrón (sirve de fondo en la escena)
    board_img = ft.Image(src=board_src, fit=ft.ImageFit.COVER, expand=True)
    # Maestra: fija a la derecha
    teacher   = ft.Image(src=teacher_src, fit=ft.ImageFit.CONTAIN) if teacher_src else None

    # --- Controles header (tal cual te gusta) ---
    dd_categoria = ft.Dropdown(
        label="Categoría",
        value="aleatoria",
        options=[ft.dropdown.Option(x) for x in ["aleatoria","animales","plantas","frutas y verduras"]],
        width=220,
    )
    rg_nivel = ft.RadioGroup(
        value="medio",
        content=ft.Row(
            [ft.Radio(value="facil", label="fácil"),
            ft.Radio(value="medio", label="medio"),
            ft.Radio(value="dificil", label="difícil")],
            spacing=12, alignment=ft.MainAxisAlignment.CENTER),
    )
    btn_empezar = ft.FilledButton("Empezar juego")
    btn_nueva   = ft.OutlinedButton("Nueva partida", disabled=True)

    # --- Zona de juego (lado izquierdo sobre el pizarrón) ---
    # Progreso
    intentos_txt = ft.Text("", size=18, color="white", weight=ft.FontWeight.BOLD)
    # Palabra (guiones/letras)
    palabra_row = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.START)
    # Entrada + probar
    entrada     = ft.TextField(label="Ingresá una letra", width=240, disabled=True, text_size=14)
    btn_probar  = ft.ElevatedButton("Probar", disabled=True)
    # Mensajes
    mensaje      = ft.Text("", size=16, color="white", weight=ft.FontWeight.BOLD)
    # Letras usadas
    usadas_row  = ft.Row(wrap=True, spacing=6, alignment=ft.MainAxisAlignment.START)

    # --- Canvas tiza (ahorcado) ---
    BASE_CANVAS_W, BASE_CANVAS_H = 280, 220
    chalk = cv.Canvas(width=BASE_CANVAS_W, height=BASE_CANVAS_H, expand=False, shapes=[])

    def clear_drawing():
        chalk.shapes.clear()
        chalk.update()

    def draw_stage(n: int):
        """Dibujo del ahorcado; en 6 queda 'ahorcado'."""
        clear_drawing()
        stroke = ft.Paint(stroke_width=5, style=ft.PaintingStyle.STROKE, color="#FFFFFF")
        # estructura
        chalk.shapes.extend([
            cv.Line(10, 200, 170, 200, paint=stroke),
            cv.Line(50, 200, 50, 20,   paint=stroke),
            cv.Line(50, 20, 150, 20,   paint=stroke),
            cv.Line(150, 20, 150, 45,  paint=stroke),
        ])
        if n >= 1: chalk.shapes.append(cv.Circle(150, 70, 20, paint=stroke))
        if n >= 2: chalk.shapes.append(cv.Line(150, 90, 150, 145, paint=stroke))
        if n >= 3: chalk.shapes.append(cv.Line(150, 105, 120, 125, paint=stroke))
        if n >= 4: chalk.shapes.append(cv.Line(150, 105, 180, 125, paint=stroke))
        if n >= 5: chalk.shapes.append(cv.Line(150, 145, 125, 185, paint=stroke))
        if n >= 6:
            chalk.shapes.append(cv.Line(150, 145, 175, 185, paint=stroke))
            chalk.shapes.append(cv.Line(150, 88, 150, 96, paint=stroke))       # nudo
            chalk.shapes.append(cv.Line(146, 92, 154, 92, paint=stroke))
            chalk.shapes.extend([                                             # ojos X
                cv.Line(142, 64, 148, 70, paint=stroke), cv.Line(148, 64, 142, 70, paint=stroke),
                cv.Line(152, 64, 158, 70, paint=stroke), cv.Line(158, 64, 152, 70, paint=stroke),
            ])
            chalk.shapes.append(cv.Line(150, 78, 150, 84, paint=stroke))      # lengua
            chalk.shapes.append(cv.Line(147, 84, 153, 84, paint=stroke))
        chalk.update()

    # ---------- Estado ----------
    palabra_orig = ""
    palabra_cmp  = ""
    letras_usadas = set()
    indices_revelados = set()
    errores = 0
    MAX_ERRORES = 6  # SIEMPRE 6

    # ---------- Render ----------
    def render_palabra():
        palabra_row.controls.clear()
        for i, ch_cmp in enumerate(palabra_cmp):
            ch_orig = palabra_orig[i]
            if ch_orig == " ":
                palabra_row.controls.append(ft.Container(width=14))
            elif i in indices_revelados or ch_cmp in letras_usadas:
                src = find_letter_asset(ch_cmp)
                palabra_row.controls.append(
                    ft.Image(src=src, width=30, height=30) if src else ft.Text(ch_orig, size=28, color="white")
                )
            else:
                palabra_row.controls.append(ft.Text("_", size=28, color="white"))
        palabra_row.update()

    def render_usadas():
        usadas_row.controls.clear()
        for l in sorted(letras_usadas):
            src = find_letter_asset(l)
            usadas_row.controls.append(ft.Image(src=src, width=22, height=22) if src else ft.Text(l, color="white", size=16))
        usadas_row.update()

    def actualizar_intentos():
        restantes = MAX_ERRORES - errores
        intentos_txt.value = f"Intentos restantes: {restantes}/{MAX_ERRORES}"
        intentos_txt.update()

    def finalizar(msg: str, color: str):
        mensaje.value, mensaje.color = msg, color
        mensaje.update()
        entrada.disabled = True; btn_probar.disabled = True
        btn_nueva.disabled = False
        entrada.update(); btn_probar.update(); btn_nueva.update()

    def check_fin():
        for i, c in enumerate(palabra_cmp):
            if c.isalpha() and (i not in indices_revelados) and (c not in letras_usadas):
                break
        else:
            finalizar(f"🎉 ¡Ganaste! Era: {palabra_orig}", "green"); return True
        if errores >= MAX_ERRORES:
            finalizar(f"💀 Perdiste. Era: {palabra_orig}", "red"); return True
        return False

    # ---------- Juego ----------
    def intentar(_=None):
        nonlocal errores
        letra_raw = (entrada.value or "").strip().lower()
        entrada.value = ""; entrada.update()

        if len(letra_raw) != 1 or not letra_raw.isalpha():
            mensaje.value, mensaje.color = "⚠️ Ingresá UNA letra válida.", "orange"; mensaje.update(); return
        letra_norm = quitar_tildes(letra_raw)[0]
        if letra_norm in letras_usadas:
            mensaje.value, mensaje.color = f"⚠️ Ya usaste '{letra_raw}'.", "orange"; mensaje.update(); return

        letras_usadas.add(letra_norm); render_usadas()
        if letra_norm in palabra_cmp:
            mensaje.value, mensaje.color = f"✅ ¡Bien! '{letra_raw}' está.", "green"
        else:
            errores += 1
            draw_stage(errores)
            mensaje.value, mensaje.color = f"❌ No está '{letra_raw}'.", "red"

        mensaje.update()
        actualizar_intentos()
        render_palabra()
        check_fin()

    def revelar_inicial(nivel: str):
        """fácil=2, medio=1, difícil=0 (sin cambiar intentos)."""
        indices_revelados.clear()
        n = 2 if nivel == "facil" else 1 if nivel == "medio" else 0
        idxs = [i for i, ch in enumerate(palabra_cmp) if ch.isalpha()]
        random.shuffle(idxs)
        for i in idxs[:min(n, len(idxs))]:
            indices_revelados.add(i)

    btn_probar.on_click = intentar
    entrada.on_submit = intentar

    def iniciar_juego(_):
        nonlocal palabra_orig, palabra_cmp, letras_usadas, errores
        letras_usadas = set(); errores = 0
        categoria = dd_categoria.value; nivel = rg_nivel.value
        palabra_orig = elegir_palabra(categoria)
        palabra_cmp  = quitar_tildes(palabra_orig).lower()
        clear_drawing()
        entrada.disabled = False; btn_probar.disabled = False; btn_nueva.disabled = False
        entrada.update(); btn_probar.update(); btn_nueva.update()
        mensaje.value = ""; mensaje.update()
        actualizar_intentos()
        revelar_inicial(nivel)
        render_usadas(); render_palabra()

    btn_empezar.on_click = iniciar_juego
    btn_nueva.on_click   = iniciar_juego

    # ====== LAYOUT ======
    header = ft.Column(
        [
            ft.Text("Juego del Ahorcado", size=28, weight=ft.FontWeight.BOLD, color="white"),
            ft.Row([dd_categoria, ft.Text("Nivel:", color="white"), rg_nivel, btn_empezar, btn_nueva],
                    alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=12),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )
    divider = ft.Divider(height=1, thickness=1, color="#373737")

    # --- Overlay (columna izquierda) que va sobre el pizarrón ---
    # Todo el juego en una columna: progreso arriba, luego filas/columnas
    game_left_col = ft.Column(
        [
            # Progreso bajo banderines
            ft.Container(intentos_txt, padding=ft.padding.only(bottom=10)),
            # Palabra
            palabra_row,
            # Entrada + Probar
            ft.Row([entrada, btn_probar], spacing=10),
            # Mensajes
            mensaje,
            # Ahorcado + letras usadas
            ft.Row(
                [
                    chalk,
                    ft.Column(
                        [
                            ft.Text("Letras usadas:", color="white", size=14),
                            usadas_row,
                        ],
                        spacing=6,
                    ),
                ],
                spacing=24,
                alignment=ft.MainAxisAlignment.START,
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # El overlay vive dentro de un Container (tamaño y padding se ajustan en on_resize)
    overlay_container = ft.Container(
        content=game_left_col,
        padding=ft.padding.only(top=100, left=70, right=70, bottom=40),
        expand=False,
        alignment=ft.alignment.top_left,
    )

    # Escena: Stack con el pizarrón de fondo a pantalla completa + fila visible con overlay y maestra
    scene_stack = ft.Stack(
        controls=[
            ft.Container(board_img, expand=True),  # fondo que llena
            # Capa superior: split izquierda/derecha
            ft.Container(
                content=ft.Row(
                    [
                        # IZQUIERDA: overlay sobre pizarrón
                        ft.Container(overlay_container, alignment=ft.alignment.top_left, expand=True),
                        # DERECHA: maestra fija, no pisa nada
                        ft.Container(
                            content=(teacher if teacher else ft.Container()),
                            alignment=ft.alignment.bottom_right,
                            expand=True,
                            padding=ft.padding.only(right=20, bottom=10),
                        ),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    expand=True,
                ),
                expand=True,
            ),
        ],
        expand=True,
    )

    # Root
    root = ft.Column(
        [header, divider, ft.Container(scene_stack, expand=True)],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    page.add(root)

    # ====== Responsividad ======
    # Usamos el ancho de la mitad izquierda para escalar padding, canvas y tamaños.
    def resize_layout(e=None):
        # Alto disponible para la escena (debajo del header)
        header_guess = 220
        avail_w = max(900, page.width)           # ancho total de ventana
        avail_h = max(500, page.height - header_guess)

        # Split 55% / 45% (un poco más de aire a la izquierda)
        left_w  = int(avail_w * 0.55)
        right_w = avail_w - left_w

        # Padding del overlay (zona segura del pizarrón) proporcional al ancho izquierdo
        # Estos coeficientes están calibrados para tu imagen; podés tocarlos fino si querés.
        s = max(0.8, min(1.6, left_w / 900))  # factor de escala suave
        overlay_container.padding = ft.padding.only(
            top=int(95 * s), left=int(60 * s), right=int(40 * s), bottom=int(30 * s)
        )
        overlay_container.width = left_w
        overlay_container.height = avail_h

        # Canvas del ahorcado escala junto con el overlay
        chalk.width  = int(BASE_CANVAS_W * s)
        chalk.height = int(BASE_CANVAS_H * s)

        # Maestra acompaña el espacio derecho
        if teacher:
            teacher.width = int(min(460, max(260, right_w * 0.70)))

        # Fuerzo updates
        overlay_container.update()
        chalk.update()
        if teacher: teacher.update()

    page.on_resize = resize_layout
    resize_layout()

ft.app(target=main, assets_dir=ASSETS_DIR)
