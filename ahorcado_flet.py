import flet as ft
import flet.canvas as cv
import os, re, random, unicodedata

# ====== Rutas ======
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR    = os.path.join(ASSETS_DIR, "images")
LETTER_DIR = os.path.join(IMG_DIR, "letters")
HANG_DIR   = os.path.join(IMG_DIR, "hangman")  # stage-01.png (pizarrón) y teacher.png

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

def find_asset_in_hangman(names: list[str]):
    for f in list_images(HANG_DIR):
        low = f.lower()
        if any(n in low for n in names):
            return rel_path(os.path.join(HANG_DIR, f))
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

    # --- Escena: pizarrón + maestra ---
    board_src   = find_asset_in_hangman(["stage-01", "pizarron", "board"])
    teacher_src = find_asset_in_hangman(["teacher", "maestra"])

    # Relación del PNG del pizarrón (1049x768 ≈ 1.366)
    BOARD_ASPECT = 1049 / 768

    # tamaños base (se recalculan en on_resize)
    BOARD_W = 820
    BOARD_H = int(BOARD_W / BOARD_ASPECT)

    board_img = ft.Image(src=board_src, width=BOARD_W, height=BOARD_H, fit=ft.ImageFit.COVER)
    teacher   = ft.Image(src=teacher_src, width=320, fit=ft.ImageFit.CONTAIN) if teacher_src else None

    # --- Controles fuera del pizarrón ---
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

    # --- Controles sobre el pizarrón (tiza) ---
    palabra_row = ft.Row(wrap=True, spacing=6, alignment=ft.MainAxisAlignment.CENTER)
    usadas_row  = ft.Row(wrap=True, spacing=4, alignment=ft.MainAxisAlignment.CENTER)
    entrada     = ft.TextField(label="Ingresá una letra", width=210, disabled=True, text_size=14)
    btn_probar  = ft.ElevatedButton("Probar", disabled=True)
    intentos_txt = ft.Text("", size=16, color="white", weight=ft.FontWeight.BOLD)
    mensaje      = ft.Text("", size=16, color="white", weight=ft.FontWeight.BOLD)

    # --- Canvas tiza (arriba-izq del pizarrón) ---
    BASE_CANVAS_W, BASE_CANVAS_H = 300, 220
    chalk = cv.Canvas(width=BASE_CANVAS_W, height=BASE_CANVAS_H, expand=False, shapes=[])

    def clear_drawing():
        chalk.shapes.clear()
        chalk.update()

    def draw_stage(n: int):
        """Dibuja paso a paso (1..6). En 6 agrega 'ahorcado' (ojos X, nudo y lengua)."""
        clear_drawing()
        stroke = ft.Paint(stroke_width=5, style=ft.PaintingStyle.STROKE, color="#FFFFFF")  # blanco tiza
        # estructura
        chalk.shapes.extend([
            cv.Line(20, 200, 180, 200, paint=stroke),
            cv.Line(60, 200, 60, 20,   paint=stroke),
            cv.Line(60, 20, 160, 20,   paint=stroke),
            cv.Line(160, 20, 160, 45,  paint=stroke),
        ])
        if n >= 1: chalk.shapes.append(cv.Circle(160, 70, 20, paint=stroke))              # cabeza
        if n >= 2: chalk.shapes.append(cv.Line(160, 90, 160, 145, paint=stroke))          # torso
        if n >= 3: chalk.shapes.append(cv.Line(160, 105, 130, 125, paint=stroke))         # brazo izq
        if n >= 4: chalk.shapes.append(cv.Line(160, 105, 190, 125, paint=stroke))         # brazo der
        if n >= 5: chalk.shapes.append(cv.Line(160, 145, 135, 185, paint=stroke))         # pierna izq
        if n >= 6:
            chalk.shapes.append(cv.Line(160, 145, 185, 185, paint=stroke))                # pierna der
            # nudo/cuerda al cuello
            chalk.shapes.append(cv.Line(160, 88, 160, 96, paint=stroke))
            chalk.shapes.append(cv.Line(156, 92, 164, 92, paint=stroke))
            # ojos en X
            chalk.shapes.extend([
                cv.Line(152, 64, 158, 70, paint=stroke), cv.Line(158, 64, 152, 70, paint=stroke),
                cv.Line(162, 64, 168, 70, paint=stroke), cv.Line(168, 64, 162, 70, paint=stroke),
            ])
            # lengua (pequeño rectángulo)
            chalk.shapes.append(cv.Line(160, 78, 160, 84, paint=stroke))
            chalk.shapes.append(cv.Line(157, 84, 163, 84, paint=stroke))
        chalk.update()

    # ---------- Estado ----------
    palabra_orig = ""
    palabra_cmp  = ""
    letras_usadas = set()
    indices_revelados = set()
    errores = 0
    MAX_ERRORES = 6

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
                    ft.Image(src=src, width=32, height=32) if src else ft.Text(ch_orig, size=30, color="white")
                )
            else:
                palabra_row.controls.append(ft.Text("_", size=30, color="white"))
        palabra_row.update()

    def render_usadas():
        usadas_row.controls.clear()
        for l in sorted(letras_usadas):
            src = find_letter_asset(l)
            usadas_row.controls.append(
                ft.Image(src=src, width=22, height=22) if src else ft.Text(l, color="white", size=16)
            )
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
        # ¿Ganó?
        for i, c in enumerate(palabra_cmp):
            if c.isalpha() and (i not in indices_revelados) and (c not in letras_usadas):
                break
        else:
            finalizar(f"🎉 ¡Ganaste! Era: {palabra_orig}", "green"); return True
        # ¿Perdió?
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
        """fácil=2, medio=1, difícil=0."""
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

        categoria = dd_categoria.value
        nivel     = rg_nivel.value

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

    # Overlay exacto dentro del área del pizarrón (padding responsive)
    overlay_padding = ft.padding.only(top=110, left=70, right=70, bottom=40)

    overlay = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        chalk,
                        ft.Column(
                            [
                                palabra_row,
                                ft.Row([entrada, btn_probar], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([intentos_txt, mensaje], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Text("Letras usadas:", color="white", size=14),
                                usadas_row,
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=30,
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=overlay_padding,
        width=BOARD_W,
        height=BOARD_H,
    )

    board_stack = ft.Stack(
        [
            ft.Container(content=board_img, width=BOARD_W, height=BOARD_H),
            overlay,
        ],
        width=BOARD_W,
        height=BOARD_H,
    )

    # Contenedores para centrar y dar “bottom” visual
    board_holder   = ft.Container(content=board_stack, alignment=ft.alignment.center, padding=10)
    teacher_holder = ft.Container(content=teacher, alignment=ft.alignment.bottom_center, padding=10) if teacher else ft.Container()

    scene = ft.Row(
        [board_holder, teacher_holder],
        wrap=True,  # si no entra, pasa la maestra abajo
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END,
        spacing=24,
    )

    root = ft.Column([header, divider, scene], spacing=12, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    page.add(root)

    # ====== Responsividad ======
    def resize_layout(e=None):
        nonlocal BOARD_W, BOARD_H
        # márgenes laterales y ancho disponible
        avail_w = max(640, page.width - 80)
        # si la pantalla es angosta, que el pizarrón ocupe ~90%; si es amplia, ~62%
        frac = 0.9 if avail_w < 1000 else 0.62
        new_board_w = int(min(900, max(560, avail_w * frac)))
        new_board_h = int(new_board_w / BOARD_ASPECT)

        BOARD_W, BOARD_H = new_board_w, new_board_h

        # tamaño maestra
        teacher_w = int(min(360, max(240, avail_w * 0.24)))
        if teacher:
            teacher.width = teacher_w
            teacher.update()

        # actualizar board y overlay
        board_img.width = BOARD_W; board_img.height = BOARD_H; board_img.update()
        overlay.width = BOARD_W; overlay.height = BOARD_H

        # padding del overlay proporcional al ancho del pizarrón
        s = BOARD_W / 820  # 820 era el ancho base
        overlay.padding = ft.padding.only(
            top=int(110 * s), left=int(70 * s), right=int(70 * s), bottom=int(40 * s)
        )
        overlay.update()

    page.on_resize = resize_layout
    resize_layout()  # primera vez

ft.app(target=main, assets_dir=ASSETS_DIR)
