import flet as ft
import os, re, random, unicodedata

# 👉 Cambiá esta ruta si tu carpeta es otra
ASSETS_DIR = "/Users/sofiamendoza/Desktop/Python/Proyecto/assets"

# =============== Utilidades ===============
def quitar_tildes(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def rel_path(abs_p: str) -> str:
    return abs_p.replace(ASSETS_DIR + os.sep, "").replace("\\", "/")

def find_dir_ci(base_dir: str, target: str, max_depth: int = 4):
    """Busca carpeta target dentro de base_dir (case-insensitive)."""
    if not os.path.isdir(base_dir):
        return None
    t = target.lower()
    base = os.path.abspath(base_dir)
    for root, dirs, _ in os.walk(base):
        if os.path.relpath(root, base).count(os.sep) > max_depth:
            dirs[:] = []
            continue
        for d in dirs:
            if d.lower() == t:
                return os.path.join(root, d)
    return None

# Localizar carpetas reales (soporta 'images'/'Images', etc.)
LETTER_DIR = find_dir_ci(ASSETS_DIR, "letters") or os.path.join(ASSETS_DIR, "images", "letters")
HANG_DIR   = find_dir_ci(ASSETS_DIR, "hangman") or os.path.join(ASSETS_DIR, "images", "hangman")

def list_images(folder):
    if not folder or not os.path.isdir(folder):
        return []
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    return [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in exts]

def find_letter_asset(letter: str):
    """
    Busca a.png ... z.png (o variantes que empiecen por la letra).
    Devuelve ruta RELATIVA (para Flet) o None.
    """
    if not LETTER_DIR or not os.path.isdir(LETTER_DIR):
        return None
    l = quitar_tildes(letter.lower())[:1]
    if not l or not l.isalpha():
        return None

    # Preferir exactamente "a.png"..."z.png" si existen
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        cand = os.path.join(LETTER_DIR, f"{l}{ext}")
        if os.path.exists(cand):
            return rel_path(cand)

    # Si no está, aceptar cualquier archivo que empiece por la letra (a-02.png, aX.webp, etc.)
    for f in sorted(list_images(LETTER_DIR)):
        base, _ = os.path.splitext(f)
        if base.lower().startswith(l):
            return rel_path(os.path.join(LETTER_DIR, f))
    return None

def find_stage_asset(stage: int):
    """Devuelve imagen para la etapa (0,1,2,...) o None."""
    if not HANG_DIR or not os.path.isdir(HANG_DIR):
        return None
    for f in list_images(HANG_DIR):
        if re.search(rf"(?:^|[^0-9]){stage}(?:[^0-9]|$)", f) or re.search(rf"stage-{stage}", f, re.I):
            return rel_path(os.path.join(HANG_DIR, f))
    return None

def infer_max_stage(default_val: int = 6) -> int:
    if not HANG_DIR or not os.path.isdir(HANG_DIR):
        return default_val
    nums = []
    for f in list_images(HANG_DIR):
        m = re.search(r"(\d+)", f)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else default_val

MAX_STAGE = infer_max_stage(6)

# =============== Palabras & Config ===============
PALABRAS = {
    "animales": ['tiburón','jirafa','elefante','león','gato','perro','cocodrilo','ballena','cebra','erizo'],
    "plantas": ['jazmín','helecho','ficus','diente de león','cactus','aloe vera','narcizo','margarita','rosa','cola de zorro'],
    "frutas y verduras": ['morrón','cebolla','zanahoria','manzana','pera','papa','tomate','frutilla','sandia','coliflor'],
}

def elegir_palabra(categoria: str) -> str:
    if categoria == "aleatoria":
        categoria = random.choice(list(PALABRAS.keys()))
    return random.choice(PALABRAS[categoria])

def indices_prim_y_ult_no_espacio(palabra: str):
    i_prim = next((i for i, ch in enumerate(palabra) if ch != " "), 0)
    i_ult  = next((i for i in range(len(palabra)-1, -1, -1) if palabra[i] != " "), len(palabra)-1)
    return i_prim, i_ult

def intentos_por_dificultad(niv: str) -> int:
    return {"facil": 8, "medio": 6, "dificil": 4}.get(niv, 6)

# =============== App ===============
def main(page: ft.Page):
    page.title = "Ahorcado - Flet"
    page.padding = 0
    page.bgcolor = "#000"

    # -------- Config --------
    dd_categoria = ft.Dropdown(
        label="Categoría",
        value="aleatoria",
        options=[ft.dropdown.Option(x) for x in ["aleatoria","animales","plantas","frutas y verduras"]],
        width=240,
    )
    rg_nivel = ft.RadioGroup(
        value="medio",
        content=ft.Row(
            [ft.Radio(value="facil", label="fácil"),
                ft.Radio(value="medio", label="medio"),
                ft.Radio(value="dificil", label="difícil")],
            spacing=18
        ),
    )
    btn_empezar = ft.FilledButton("Empezar juego")

    # -------- Estado --------
    palabra_orig = ""
    palabra_cmp = ""
    letras_usadas = set()
    indices_revelados = set()
    intentos = 0
    MAX_INTENTOS = 6

    # -------- Fondo (stage) --------
    stage0 = find_stage_asset(0)
    if stage0:
        bg = ft.Image(src=stage0, fit=ft.ImageFit.COVER, expand=True)
        def set_stage(n: int):
            src = find_stage_asset(n)
            if src:
                bg.src = src; bg.update()
    else:
        bg = ft.Container(expand=True, bgcolor="#111")
        def set_stage(n: int): pass

    # -------- Overlay --------
    palabra_row = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    usadas_row  = ft.Row(wrap=True, spacing=6, alignment=ft.MainAxisAlignment.CENTER)
    entrada     = ft.TextField(label="Ingresá una letra", width=180, disabled=True)
    btn_probar  = ft.ElevatedButton("Probar", disabled=True)
    mensaje     = ft.Text("", size=16, color="white")

    def render_palabra():
        palabra_row.controls.clear()
        for i, ch_cmp in enumerate(palabra_cmp):
            ch_orig = palabra_orig[i]
            if ch_orig == " ":
                palabra_row.controls.append(ft.Container(width=22))
            elif i in indices_revelados or ch_cmp in letras_usadas:
                src = find_letter_asset(ch_cmp)
                palabra_row.controls.append(
                    ft.Image(src=src, width=34, height=34) if src else ft.Text(ch_orig, size=32, color="white")
                )
            else:
                palabra_row.controls.append(ft.Text("_", size=32, color="white"))
        palabra_row.update()

    def render_usadas():
        usadas_row.controls.clear()
        for l in sorted(letras_usadas):
            src = find_letter_asset(l)
            usadas_row.controls.append(ft.Image(src=src, width=22, height=22) if src else ft.Text(l, color="white"))
        usadas_row.update()

    def finalizar(msg: str, color: str):
        mensaje.value, mensaje.color = msg, color
        mensaje.update()
        entrada.disabled = True; btn_probar.disabled = True
        entrada.update(); btn_probar.update()

    def check_fin():
        ok = True
        for i, c in enumerate(palabra_cmp):
            if c.isalpha() and c not in letras_usadas and i not in indices_revelados:
                ok = False; break
        if ok:
            finalizar(f"🎉 ¡Ganaste! Era: {palabra_orig}", "green"); return True
        if intentos >= MAX_INTENTOS:
            finalizar(f"💀 Perdiste. Era: {palabra_orig}", "red"); return True
        return False

    def intentar(_=None):
        nonlocal intentos
        letra_raw = (entrada.value or "").strip().lower()
        entrada.value = ""; entrada.update()

        if len(letra_raw) != 1 or not quitar_tildes(letra_raw).isalpha():
            mensaje.value, mensaje.color = "⚠️ Ingresá UNA letra válida.", "orange"; mensaje.update(); return
        letra = quitar_tildes(letra_raw)[0]
        if letra in letras_usadas:
            mensaje.value, mensaje.color = f"⚠️ Ya usaste '{letra_raw}'.", "orange"; mensaje.update(); return

        letras_usadas.add(letra); render_usadas()

        if letra in palabra_cmp:
            mensaje.value, mensaje.color = f"✅ ¡Bien! '{letra_raw}' está.", "green"; mensaje.update()
        else:
            intentos += 1; set_stage(intentos)
            mensaje.value, mensaje.color = f"❌ No está '{letra_raw}'. Intentos {intentos}/{MAX_INTENTOS}", "red"; mensaje.update()

        render_palabra(); check_fin()

    btn_probar.on_click = intentar
    entrada.on_submit = intentar

    def iniciar_juego(_):
        nonlocal palabra_orig, palabra_cmp, letras_usadas, indices_revelados, intentos, MAX_INTENTOS
        letras_usadas = set(); indices_revelados = set(); intentos = 0

        categoria = dd_categoria.value
        nivel = rg_nivel.value

        palabra_orig = elegir_palabra(categoria)
        palabra_cmp = quitar_tildes(palabra_orig).lower()

        # revelado inicial (como tu script)
        i_prim, i_ult = indices_prim_y_ult_no_espacio(palabra_orig)
        letras_unicas_norm = {quitar_tildes(ch.lower()) for ch in palabra_orig if ch != " "}
        if nivel == "facil":
            if len(letras_unicas_norm) == 1: indices_revelados.add(i_prim)
            else: indices_revelados.update({i_prim, i_ult})
        elif nivel == "medio":
            indices_revelados.add(i_ult)

        MAX_INTENTOS = min(intentos_por_dificultad(nivel), MAX_STAGE)

        entrada.disabled = False; btn_probar.disabled = False
        entrada.update(); btn_probar.update()
        set_stage(0)
        mensaje.value = ""; mensaje.update()
        render_usadas(); render_palabra()

    btn_empezar.on_click = iniciar_juego

    # Panel translúcido centrado
    overlay_panel = ft.Container(
        padding=20,
        border_radius=12,
        bgcolor="#00000066",  # negro con transparencia
        width=680,
        content=ft.Column(
            [
                ft.Text("Juego del Ahorcado", size=36, weight=ft.FontWeight.BOLD, color="white"),
                ft.Row([dd_categoria, ft.Text("Nivel:", color="white"), rg_nivel], spacing=16),
                btn_empezar,
                ft.Container(height=8),
                ft.Row([palabra_row], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Row([entrada, btn_probar], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                mensaje,
                ft.Container(height=8),
                ft.Text("Letras usadas:", color="white"),
                usadas_row,
            ],
            spacing=10,
        ),
    )

    page.add(
        ft.Stack(
            [
                bg,
                ft.Column(
                    [ft.Row([overlay_panel], alignment=ft.MainAxisAlignment.CENTER)],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                ),
            ],
            expand=True,
        )
    )

ft.app(target=main, assets_dir=ASSETS_DIR)
