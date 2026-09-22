import json, os, datetime, random, math

ROOT = os.path.join(os.path.dirname(__file__), "project")
os.makedirs(ROOT, exist_ok=True)

# ---------- themes ----------
LIGHT = dict(
    bg="#F4EDDF", surface="#FCF8F0", surface2="#EFE7D6", ink="#1F1C16", muted="#5F594E",
    border="#D9CFBC", green="#1E5A3A", greenInk="#174A2F", greenBg="#E1ECE2", greenSoft="#C9DECD",
    red="#9A2A2A", redBg="#F5E1DD", redSoft="#E8C4BE", amber="#8A5A0B", amberBg="#F3E6C6", amberInk="#B8791A",
    dim="0.55", onGreen="#F4EDDF",
)
DARK = dict(
    bg="#1B1915", surface="#26231D", surface2="#302C25", ink="#EFE8DA", muted="#B3AB9C",
    border="#3E3931", green="#7FC498", greenInk="#9FD6B3", greenBg="#20312A", greenSoft="#2C4A3A",
    red="#E68F84", redBg="#3B2724", redSoft="#5A332E", amber="#E0B460", amberBg="#3A3020", amberInk="#E0B460",
    dim="0.45", onGreen="#1B1915",
)
PRINT = dict(LIGHT, bg="#FFFFFF", surface="#FFFFFF", surface2="#F2F2F2", ink="#111111", muted="#555555", border="#BBBBBB")

SERIF = "'Fraunces', Georgia, serif"
SANS = "'Source Sans 3', 'Helvetica Neue', sans-serif"
MONO = "'IBM Plex Mono', 'Courier New', monospace"

# ---------- copy ----------
EN = dict(
    lang="en", app="Student Meal Planner", tag="Mercadona · Spain",
    yourWeek="Your week", presets="Quick start", budget="Grocery budget", people="People", days="Days", meals="Meals to plan",
    breakfast="Breakfast", lunch="Lunch", dinner="Dinner", diet="Diet",
    diets=["Everything", "Pescatarian", "Vegetarian", "Vegan"],
    allergies="Allergies", allergiesPh="Add an allergy…", home="Already at home", homePh="Add…",
    avoid="Don't want", avoidPh="Add…", note="Anything else", notePh="Tiny kitchen, one pan, no oven.",
    hint="≈ {pm} per person per meal · {n} meals", hintLow="≈ {pm} per person per meal · {n} meals · below our €0.85 floor",
    submit="Plan my meals", fine="Prices come from Mercadona packages. Every total is added up by code — the AI never touches a price.",
    how="How it works", howSub="Five steps. Two are AI, three are plain code.",
    who=dict(you="You", ai="AI", code="Code"),
    steps=[
        ("you", "You set the budget, people, days and what you already have.", ""),
        ("ai", "The model drafts meals that reuse ingredients across days.", "It writes the recipes. It never sees or invents a price."),
        ("code", "Each ingredient is matched to a real Mercadona package.", "Whole packages only: you can't buy 300 g of a 1 kg bag."),
        ("code", "Package prices are summed; leftovers are computed.", "Needed − bought = what's left in your fridge."),
        ("code", "The total is checked against your budget.", "Within, over, or not realistic — decided by arithmetic, not by the model."),
    ],
    heroTitle="One week, fourteen ingredients, nothing thrown away.",
    heroSub="Every strand is an ingredient. It opens on the day you first cook it, runs through every day it's reused, and either ends clean or trails off as a leftover. This is what your plan will look like.",
    promise="Whole packages, honest totals",
    promiseBody="Most planners price 200 g of rice. You buy a 1 kg bag. We price the bag, and show you what's left over so the next plan can use it.",
    loadingTitle="Planning 10 meals for 2 people…", loadingSub="Usually 15–30 seconds. Recipes are being written, then priced.",
    elapsed="12 s", loadSteps=[("done", "Read your constraints"), ("done", "Drafted 10 meals that share ingredients"), ("active", "Matching 14 ingredients to Mercadona packages"), ("todo", "Adding up whole packages"), ("todo", "Checking the total against €40")],
    loadMsg="Matching «garbanzos cocidos» → bote 400 g, €0.65", loadDay="Day 3 of 5 — carrying the pantry forward",
    within="Within budget", over="Over budget", notreal="Not realistic",
    of="of", left="left", overBy="over by",
    perMeal="per person per meal", leftoverVal="of food left over", reuse="ingredients used twice or more",
    perMealSub="20 meals · 2 people · 5 days",
    leftoverSub="11% of the basket — mostly rice and lentils, fine in the cupboard",
    reuseSub="onion, rice and chickpeas do the heavy lifting",
    mapTitle="Reuse map", mapSub="Each strand is one ingredient: opened, cooked (knots), and what's left (amber).",
    legendKnot="cooked that day", legendBead="left over, sized by how much", legendDash="from your pantry",
    costByDay="Cost of what's opened each day",
    shelfTitle="What's left on Friday", shelfSub="Worth about €4.10. Next week's plan starts from here, so nothing is wasted.",
    keeps="Keeps in the cupboard", fridge="Use within the week", planNext="Plan next week from these leftovers",
    keepsItems=["Rice 700 g", "Lentils 500 g", "Spaghetti 500 g", "Carrots 700 g", "Garlic 2 heads"],
    fridgeItems=["Onion 400 g", "Potatoes 1.2 kg", "Tomatoes 300 g", "Courgette 400 g", "Eggs 2", "Cheese 50 g", "Tuna 1 tin"],
    planTitle="Your 5 days", planSub="Lunch and dinner · 2 people · everything, no nuts, no mushrooms",
    dayNames=["Mon", "Tue", "Wed", "Thu", "Fri"], day="Day",
    lunchL="Lunch", dinnerL="Dinner", uses="uses", reusedFrom="reused from", leftoverTo="leftover →",
    ingredients="Ingredients", method="Method", min="min",
    receiptTitle="Shopping list", receiptSub="Whole packages · Mercadona", copy="Copy", print="Print",
    colItem="Item", colNeed="Need", colBuy="Buy", colLeft="Left", colCost="€",
    atHome="at home", subtotal="Subtotal", budgetL="Budget", remaining="Remaining", overL="Over",
    itemsCount="20 items · 18 packages",
    changeTitle="What you can change", changeSub="Each one is computed from the same package prices. Pick one, we re-plan.",
    changes=[
        ("Swap the two chicken dinners for lentil and egg dishes", "−€5.90", "Chicken is 22% of the basket. Lentils and eggs cover the same meals."),
        ("Plan 4 days instead of 5", "−€7.10", "Friday drops off; leftovers shrink too."),
        ("Skip apples and yoghurt", "−€3.14", "They only appear once each. Fruit from home would cover it."),
    ],
    apply="Apply", overHint="You're €6.80 over. One change below is enough.",
    nrTitle="We can't plan this honestly", nrSub="€12 for 2 people, 7 days, 3 meals a day is 42 meals — about €0.29 per person per meal.",
    nrWhy="Why", nrReasons=[
        "The cheapest full meal we can build from whole Mercadona packages is about €0.85 per person.",
        "42 meals × €0.85 = €35.70 before any waste.",
        "Even the smallest 7-day basket in whole packages (rice, eggs, lentils, oil) is around €19.",
    ],
    nrTry="Try one of these", nrOpts=[
        ("Raise the budget to €38", "Same 7 days, all three meals."),
        ("Keep €12, plan 2 days", "Lunch and dinner only, for 2 people."),
        ("Cook for 1, 3 days", "Everything you set, just one person."),
        ("Tell us what's at home", "Rice, oil, pasta already there cut the basket a lot."),
    ],
    nrNo="No plan was generated. We'd rather say so than hand you a list you can't afford.",
    newPlan="New plan", edit="Edit", recipes="Recipes by AI · totals by code",
    aisles=["Fruit & vegetables", "Meat", "Eggs & dairy", "Rice, pasta & pulses", "Pantry"],
    printFor="Plan for", printTick="Tick as you shop", mealsWord="meals",
)
ES = dict(EN)
ES.update(
    lang="es", tag="Mercadona · España",
    yourWeek="Tu semana", presets="Empezar rápido", budget="Presupuesto de compra", people="Personas", days="Días", meals="Comidas a planificar",
    breakfast="Desayuno", lunch="Comida", dinner="Cena", diet="Dieta",
    diets=["De todo", "Pescetariana", "Vegetariana", "Vegana"],
    allergies="Alergias", allergiesPh="Añadir…", home="Ya tengo en casa", homePh="Añadir…",
    avoid="No quiero", avoidPh="Añadir…", note="Algo más", notePh="Cocina pequeña, una sartén, sin horno.",
    hint="≈ {pm} por persona y comida · {n} comidas", hintLow="≈ {pm} por persona y comida · {n} comidas · por debajo de nuestro mínimo de 0,85 €",
    submit="Planificar mis comidas", fine="Los precios vienen de envases de Mercadona. Cada total lo suma el código: la IA nunca toca un precio.",
    how="Cómo funciona", howSub="Cinco pasos. Dos son IA, tres son código.",
    who=dict(you="Tú", ai="IA", code="Código"),
    steps=[
        ("you", "Tú pones presupuesto, personas, días y lo que ya tienes.", ""),
        ("ai", "El modelo propone comidas que reutilizan ingredientes.", "Escribe las recetas. Nunca ve ni inventa un precio."),
        ("code", "Cada ingrediente se asocia a un envase real de Mercadona.", "Solo envases enteros: no puedes comprar 300 g de una bolsa de 1 kg."),
        ("code", "Se suman los envases y se calculan las sobras.", "Necesario − comprado = lo que queda en tu nevera."),
        ("code", "El total se compara con tu presupuesto.", "Dentro, por encima o no realista: lo decide la aritmética, no el modelo."),
    ],
    heroTitle="Una semana, catorce ingredientes, nada a la basura.",
    heroSub="Cada hilo es un ingrediente. Se abre el día que lo cocinas por primera vez, sigue por cada día en que se reutiliza y termina limpio o se queda como sobra. Así será tu plan.",
    promise="Envases enteros, totales honestos",
    promiseBody="La mayoría de planificadores valoran 200 g de arroz. Tú compras la bolsa de 1 kg. Nosotros valoramos la bolsa y te enseñamos lo que sobra para el siguiente plan.",
    loadingTitle="Planificando 10 comidas para 2 personas…", loadingSub="Suele tardar 15–30 segundos. Primero se escriben las recetas, luego se valoran.",
    loadSteps=[("done", "Leídas tus condiciones"), ("done", "Propuestas 10 comidas que comparten ingredientes"), ("active", "Asociando 14 ingredientes a envases de Mercadona"), ("todo", "Sumando envases enteros"), ("todo", "Comparando el total con 40 €")],
    loadMsg="Asociando «garbanzos cocidos» → bote 400 g, 0,65 €", loadDay="Día 3 de 5 — arrastrando la despensa",
    within="Dentro del presupuesto", over="Por encima del presupuesto", notreal="No es realista",
    of="de", left="sobran", overBy="te pasas",
    perMeal="por persona y comida", leftoverVal="en comida que sobra", reuse="ingredientes usados dos o más veces",
    perMealSub="20 comidas · 2 personas · 5 días",
    leftoverSub="11 % de la cesta: sobre todo arroz y lentejas, aguantan en la despensa",
    reuseSub="cebolla, arroz y garbanzos hacen casi todo el trabajo",
    mapTitle="Mapa de reutilización", mapSub="Cada hilo es un ingrediente: abierto, cocinado (nudos) y lo que sobra (ámbar).",
    legendKnot="cocinado ese día", legendBead="sobra, según cuánto", legendDash="de tu despensa",
    costByDay="Coste de lo que se abre cada día",
    shelfTitle="Lo que queda el viernes", shelfSub="Vale unos 4,10 €. El plan de la semana que viene empieza aquí, así no se tira nada.",
    keeps="Aguanta en la despensa", fridge="Usar esta semana", planNext="Planificar la semana que viene con estas sobras",
    keepsItems=["Arroz 700 g", "Lentejas 500 g", "Espaguetis 500 g", "Zanahorias 700 g", "Ajos 2 cabezas"],
    fridgeItems=["Cebolla 400 g", "Patatas 1,2 kg", "Tomates 300 g", "Calabacín 400 g", "Huevos 2", "Queso 50 g", "Atún 1 lata"],
    planTitle="Tus 5 días", planSub="Comida y cena · 2 personas · de todo, sin frutos secos, sin champiñones",
    dayNames=["Lun", "Mar", "Mié", "Jue", "Vie"], day="Día",
    lunchL="Comida", dinnerL="Cena", uses="usa", reusedFrom="reutilizado de", leftoverTo="sobra →",
    ingredients="Ingredientes", method="Preparación",
    receiptTitle="Lista de la compra", receiptSub="Envases enteros · Mercadona", copy="Copiar", print="Imprimir",
    colItem="Artículo", colNeed="Nec.", colBuy="Compra", colLeft="Sobra", colCost="€",
    atHome="en casa", subtotal="Subtotal", budgetL="Presupuesto", remaining="Te sobran", overL="Te pasas",
    itemsCount="20 artículos · 18 envases",
    changeTitle="Qué puedes cambiar", changeSub="Cada opción sale de los mismos precios de envase. Elige una y replanificamos.",
    changes=[
        ("Cambia las dos cenas de pollo por lentejas y huevos", "−5,90 €", "El pollo es el 22 % de la cesta. Lentejas y huevos cubren las mismas comidas."),
        ("Planifica 4 días en vez de 5", "−7,10 €", "Cae el viernes; también sobra menos."),
        ("Quita manzanas y yogur", "−3,14 €", "Solo aparecen una vez cada uno. Fruta de casa lo cubre."),
    ],
    apply="Aplicar", overHint="Te pasas 6,80 €. Con un cambio de abajo basta.",
    nrTitle="No podemos planificar esto con honestidad", nrSub="12 € para 2 personas, 7 días, 3 comidas al día son 42 comidas: unos 0,29 € por persona y comida.",
    nrWhy="Por qué", nrReasons=[
        "La comida completa más barata que podemos montar con envases enteros de Mercadona cuesta unos 0,85 € por persona.",
        "42 comidas × 0,85 € = 35,70 € antes de cualquier desperdicio.",
        "Incluso la cesta mínima de 7 días en envases enteros (arroz, huevos, lentejas, aceite) ronda los 19 €.",
    ],
    nrTry="Prueba una de estas", nrOpts=[
        ("Sube el presupuesto a 38 €", "Mismos 7 días, las tres comidas."),
        ("Mantén 12 €, planifica 2 días", "Solo comida y cena, para 2 personas."),
        ("Cocina para 1, 3 días", "Todo lo que pusiste, para una persona."),
        ("Dinos qué tienes en casa", "Arroz, aceite o pasta que ya tengas reducen mucho la cesta."),
    ],
    nrNo="No se ha generado ningún plan. Preferimos decirlo a darte una lista que no puedes pagar.",
    newPlan="Nuevo plan", edit="Editar", recipes="Recetas por IA · totales por código",
    aisles=["Frutas y verduras", "Carne", "Huevos y lácteos", "Arroz, pasta y legumbres", "Despensa"],
    printFor="Plan para", printTick="Marca al comprar", mealsWord="comidas",
)

def eur(v, L):
    s = f"{v:,.2f}"
    if L["lang"] == "es":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return s + " €"
    return "€" + s

def num(v, L):
    s = f"{v:.2f}"
    return s.replace(".", ",") if L["lang"] == "es" else s

# ---------- icons ----------
def ico(name, size=16, color="currentColor", sw=2):
    paths = dict(
        check='<polyline points="20 6 9 17 4 12"/>',
        chevD='<polyline points="6 9 12 15 18 9"/>',
        chevR='<polyline points="9 6 15 12 9 18"/>',
        chevL='<polyline points="15 6 9 12 15 18"/>',
        sun='<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
        moon='<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
        copy='<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
        print='<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
        alert='<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        x='<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        arrowR='<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
        loop='<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
        minus='<line x1="5" y1="12" x2="19" y2="12"/>',
        plus='<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        clock='<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        edit='<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    )[name]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink: 0;">{paths}</svg>')

# =====================================================================
# THREADED PANTRY — the braid, drawn as inline SVG
# =====================================================================
def gen_strands(seed, n, D, reuse=0.65, leftover=0.55, pantry=0.15):
    r = random.Random(seed)
    out = []
    for i in range(n):
        w = 0.22 + (r.random() ** 1.5) * 0.78
        home = r.random() < pantry
        open_ = 0 if home else int((r.random() ** 1.3) * D)
        max_span = D - open_
        span_exp = 1.7 - reuse * 1.3
        span = 1 + int((r.random() ** span_exp) * max_span)
        if home: span = max(span, min(D, 2 + int(r.random() * D)))
        span = min(span, max_span)
        last = open_ + span - 1
        uses = {open_, last}
        for d in range(open_ + 1, last):
            if r.random() < reuse * 0.8: uses.add(d)
        lo = (0.12 + r.random() * 0.6) if r.random() < leftover else 0
        out.append(dict(open=open_, last=last, uses=uses, weight=w, leftover=lo * (0.5 if home else 1), home=home, name=""))
    out.sort(key=lambda s: (s["open"], -s["weight"]))
    return out

def braid_svg(W, H, strands, D, T, labels=False, progress=None, day_costs=None, L=None, uid="b", scale=1.0, day_label=True):
    MX = 150 if labels else 40
    MR = 60
    MT = 22
    MB = 46 if day_label else 20
    if day_costs: MB += 74
    top, bottom = MT, H - MB
    usable = bottom - top
    inkG, inkA, paper = T["green"], T["amberInk"], T["bg"]
    n = len(strands)

    def dayX(d):
        return MX + (W - MX - MR) * (0.5 if D == 1 else d / (D - 1))

    # lanes
    lanes = []
    if labels:
        rowH = usable / max(n, 1)
        for d in range(D):
            lanes.append({i: top + (i + 0.5) * rowH for i in range(n)})
    else:
        for d in range(D):
            alive = [(i, s) for i, s in enumerate(strands) if s["open"] <= d <= s["last"]]
            tw = sum(s["weight"] for _, s in alive) or 1
            y = top; m = {}
            for i, s in alive:
                h = usable * (0.35 / max(len(alive), 1) + 0.65 * s["weight"] / tw)
                m[i] = y + h / 2; y += h
            shift = (usable - (y - top)) / 2
            lanes.append({k: v + shift for k, v in m.items()})

    def sw(s):
        base = (2.2 + (s["weight"] ** 1.2) * 13) * scale
        return min(base, (usable / max(n, 1)) * 0.55) if labels else base

    parts = []
    # day rules + labels
    for d in range(D):
        x = dayX(d)
        parts.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{bottom + 10}" stroke="{inkG}" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="1 7" stroke-linecap="round"/>')
        if day_label:
            lbl = (f'{L["day"].upper() if L else "DAY"} {d + 1}')
            parts.append(f'<text x="{x:.1f}" y="{bottom + 30}" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{inkG}" fill-opacity="0.8">{lbl}</text>')
    # strands
    body = []
    for i, s in enumerate(strands):
        pts = [(dayX(d), lanes[d][i]) for d in range(s["open"], s["last"] + 1)]
        w = sw(s)
        op = 0.72 + s["weight"] * 0.26
        if s["home"] and not labels:
            x0, y0 = pts[0]
            body.append(f'<line x1="12" y1="{y0:.1f}" x2="{x0 - 8:.1f}" y2="{y0:.1f}" stroke="{inkG}" stroke-opacity="0.45" stroke-width="{max(1.5, w * 0.5):.1f}" stroke-dasharray="7 7" stroke-linecap="round"/>')
        if len(pts) > 1:
            dpath = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}'
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                dx = (bx - ax) * 0.42
                dpath += f' C {ax + dx:.1f} {ay:.1f}, {bx - dx:.1f} {by:.1f}, {bx:.1f} {by:.1f}'
            dash = ' stroke-dasharray="7 7"' if (s["home"] and labels) else ""
            body.append(f'<path d="{dpath}" fill="none" stroke="{inkG}" stroke-opacity="{op:.2f}" stroke-width="{w:.1f}" stroke-linecap="round"{dash}/>')
        ex, ey = pts[-1]
        if s["leftover"] > 0:
            ln = 24 + s["leftover"] * 46; dr = 12 + s["leftover"] * 30
            body.append(f'<path d="M {ex:.1f} {ey:.1f} C {ex + ln * 0.55:.1f} {ey:.1f}, {ex + ln * 0.7:.1f} {ey + dr * 0.7:.1f}, {ex + ln:.1f} {ey + dr:.1f}" fill="none" stroke="{inkA}" stroke-opacity="0.9" stroke-width="{max(1.6, w * 0.45):.1f}" stroke-linecap="round"/>')
            body.append(f'<circle cx="{ex + ln:.1f}" cy="{ey + dr:.1f}" r="{(2.5 + s["leftover"] * 8) * scale:.1f}" fill="{inkA}"/>')
        elif not s["home"]:
            body.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{w * 0.55:.1f}" fill="{inkG}" fill-opacity="{op:.2f}"/>')
        for d in sorted(s["uses"]):
            x = dayX(d); y = lanes[d][i]
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(3, w * 0.48):.1f}" fill="{paper}" stroke="{inkG}" stroke-opacity="{op:.2f}" stroke-width="{max(1.5, w * 0.28):.1f}"/>')
        if labels:
            body.append(f'<text x="{MX - 14}" y="{lanes[0][i] + 4:.1f}" text-anchor="end" font-family="{SANS}" font-size="13" fill="{T["ink"]}">{s["name"]}</text>')
    if progress is not None:
        px = (W - 20) * progress
        parts.append(f'<clipPath id="{uid}clip"><rect x="0" y="0" width="{px:.1f}" height="{H}"/></clipPath>')
        parts.append(f'<g clip-path="url(#{uid}clip)">{"".join(body)}</g>')
        parts.append(f'<line x1="{px:.1f}" y1="{top - 16}" x2="{px:.1f}" y2="{bottom + 16}" stroke="{inkG}" stroke-opacity="0.6" stroke-width="1.5"/>')
    else:
        parts.extend(body)
    if day_costs:
        mx = max(day_costs); bh = 44; by = H - 22
        for d, c in enumerate(day_costs):
            x = dayX(d); h = bh * c / mx
            parts.append(f'<rect x="{x - 16:.1f}" y="{by - h:.1f}" width="32" height="{h:.1f}" rx="3" fill="{inkG}" fill-opacity="0.85"/>')
            parts.append(f'<text x="{x:.1f}" y="{by - h - 6:.1f}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{T["ink"]}">{num(c, L)}</text>')
        parts.append(f'<text x="{MX if labels else 40}" y="{by + 14}" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{T["muted"]}">{L["costByDay"].upper()}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Ingredient reuse map" style="display: block; width: 100%; height: auto;">'
            f'{"".join(parts)}</svg>')

# real plan strands (days 0..4)
def real_strands(L):
    names_en = ["olive oil", "onion", "rice", "potatoes", "lentils", "eggs", "tomatoes", "red pepper", "chickpeas", "chicken breast", "courgette", "garlic", "tomato sauce", "spaghetti", "tuna", "carrots", "chicken thighs"]
    names_es = ["aceite de oliva", "cebolla", "arroz", "patatas", "lentejas", "huevos", "tomates", "pimiento rojo", "garbanzos", "pechuga de pollo", "calabacín", "ajo", "tomate frito", "espaguetis", "atún", "zanahorias", "muslos de pollo"]
    spec = [  # uses, weight, leftover, home
        ({0, 1, 2, 3, 4}, 0.25, 0.0, True),
        ({0, 1, 2}, 0.5, 0.4, False),
        ({0, 1, 4}, 0.6, 0.45, True),
        ({0, 3}, 0.85, 0.4, False),
        ({0, 2}, 0.5, 0.5, False),
        ({0, 4}, 0.5, 0.17, False),
        ({0, 3}, 0.4, 0.3, False),
        ({0, 4}, 0.3, 0.0, False),
        ({1, 3}, 0.4, 0.0, False),
        ({1}, 0.75, 0.08, False),
        ({1, 4}, 0.4, 0.4, False),
        ({1, 3}, 0.2, 0.6, False),
        ({1, 2}, 0.3, 0.0, False),
        ({2, 4}, 0.5, 0.5, False),
        ({2, 3}, 0.3, 0.33, False),
        ({2}, 0.3, 0.7, False),
        ({3}, 0.8, 0.0, False),
    ]
    names = names_en if L["lang"] == "en" else names_es
    return [dict(open=min(u), last=max(u), uses=u, weight=w, leftover=lo, home=h, name=nm) for nm, (u, w, lo, h) in zip(names, spec)]

HERO_STRANDS = gen_strands(2209, 14, 5)

# ---------- primitives ----------
def head(title, L, T, w, h):
    return f'''<!doctype html>
<html lang="{L['lang']}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&amp;family=Source+Sans+3:wght@400;600&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;font-family:{SANS};color:{T['ink']};background:{T['bg']};-webkit-font-smoothing:antialiased}}
a{{color:{T['green']}}}a:hover{{color:{T['greenInk']}}}
input,textarea,button{{font-family:inherit}}
</style>
</helmet>
<div style="width: {w}px; height: {h}px; box-sizing: border-box; background: {T['bg']}; color: {T['ink']}; font-family: {SANS}; font-size: 16px; line-height: 1.45; display: flex; flex-direction: column; overflow: hidden;">
'''

def tail(w, h):
    return f'''</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''

def topbar(L, T, mobile=False, dark=False):
    pad = "14px 16px" if mobile else "20px 48px"
    other = "ES" if L["lang"] == "en" else "EN"
    cur = "EN" if L["lang"] == "en" else "ES"
    theme_icon = ico("sun" if dark else "moon", 18, T["ink"], 1.8)
    ws = "21px" if mobile else "26px"
    return f'''<header style="display: flex; align-items: center; justify-content: space-between; padding: {pad}; border-bottom: 1px solid {T['border']}; gap: 12px; flex-shrink: 0;">
  <div style="display: flex; flex-direction: column; gap: 2px; min-width: 0;">
    <div style="font-family: {SERIF}; font-size: {ws}; font-weight: 600; font-style: italic; letter-spacing: -0.01em; color: {T['ink']}; line-height: 1.1; white-space: nowrap;">{L['app']}</div>
    <div style="font-size: 13px; color: {T['muted']};">{L['tag']}</div>
  </div>
  <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
    <div role="group" aria-label="Language" style="display: flex; border: 1px solid {T['border']}; border-radius: 999px; padding: 3px; background: {T['surface']};">
      <button type="button" aria-pressed="true" style="min-height: 36px; padding: 0 12px; border-radius: 999px; border: 0; background: {T['green']}; color: {T['onGreen']}; font-weight: 600; font-size: 14px; cursor: pointer;">{cur}</button>
      <button type="button" aria-pressed="false" style="min-height: 36px; padding: 0 12px; border-radius: 999px; border: 0; background: transparent; color: {T['ink']}; font-weight: 600; font-size: 14px; cursor: pointer;">{other}</button>
    </div>
    <button type="button" aria-label="Toggle dark mode" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 999px; border: 1px solid {T['border']}; background: {T['surface']}; cursor: pointer;">{theme_icon}</button>
  </div>
</header>
'''

def label(text, T):
    return f'<div style="font-size: 13px; font-weight: 600; color: {T["muted"]}; letter-spacing: 0.04em; text-transform: uppercase;">{text}</div>'

def field(lbl, inner, T, for_id=None, hint=None):
    tag = f'<label for="{for_id}" style="font-size: 13px; font-weight: 600; color: {T["muted"]}; letter-spacing: 0.04em; text-transform: uppercase;">{lbl}</label>' if for_id else label(lbl, T)
    h = f'<div style="font-family: {MONO}; font-size: 12.5px; color: {T["muted"]};">{hint}</div>' if hint else ""
    return f'<div style="display: flex; flex-direction: column; gap: 8px;">{tag}{inner}{h}</div>'

def inp(id_, value, T, prefix=None, placeholder="", type_="text"):
    pre = f'<span style="color: {T["muted"]}; font-size: 18px; padding-right: 8px;">{prefix}</span>' if prefix else ""
    return (f'<div style="display: flex; align-items: center; min-height: 48px; padding: 0 14px; border: 1px solid {T["border"]}; border-radius: 10px; background: {T["surface"]}; box-sizing: border-box;">{pre}'
            f'<input id="{id_}" type="{type_}" value="{value}" placeholder="{placeholder}" style="flex-grow: 1; min-width: 0; border: 0; background: transparent; font-size: 18px; color: {T["ink"]}; outline: none; padding: 0;"></div>')

def stepper(id_, value, T):
    btn = f'border: 0; background: {T["surface2"]}; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: {T["ink"]};'
    return (f'<div style="display: flex; align-items: center; gap: 6px; min-height: 48px; padding: 3px; border: 1px solid {T["border"]}; border-radius: 10px; background: {T["surface"]};">'
            f'<button type="button" aria-label="Decrease" style="{btn}">{ico("minus", 16, T["ink"])}</button>'
            f'<input id="{id_}" type="number" value="{value}" style="flex-grow: 1; width: 40px; min-width: 0; text-align: center; border: 0; background: transparent; font-size: 18px; color: {T["ink"]}; outline: none;">'
            f'<button type="button" aria-label="Increase" style="{btn}">{ico("plus", 16, T["ink"])}</button></div>')

def checkchip(id_, text, checked, T):
    bg = T["greenBg"] if checked else T["surface"]; bd = T["green"] if checked else T["border"]
    chk = "checked " if checked else ""
    return (f'<label for="{id_}" style="display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 14px; border: 1px solid {bd}; border-radius: 10px; background: {bg}; cursor: pointer; font-weight: 600; font-size: 15px; color: {T["ink"]};">'
            f'<input id="{id_}" type="checkbox" {chk}style="width: 18px; height: 18px; margin: 0; accent-color: {T["green"]};">{text}</label>')

def segmented(options, active, T):
    parts = []
    for i, o in enumerate(options):
        on = i == active
        parts.append(f'<button type="button" aria-pressed="{str(on).lower()}" style="flex-grow: 1; min-height: 40px; padding: 0 8px; border: 0; border-radius: 8px; background: {T["green"] if on else "transparent"}; color: {T["onGreen"] if on else T["ink"]}; font-weight: 600; font-size: 14px; cursor: pointer;">{o}</button>')
    return f'<div role="group" style="display: flex; gap: 3px; padding: 3px; border: 1px solid {T["border"]}; border-radius: 10px; background: {T["surface"]};">{"".join(parts)}</div>'

def chips(id_, items, placeholder, T):
    cs = "".join(
        f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 5px 6px 5px 12px; border-radius: 999px; background: {T["surface2"]}; font-size: 14px; font-weight: 600; color: {T["ink"]};">{it}'
        f'<button type="button" aria-label="Remove {it}" style="width: 24px; height: 24px; border: 0; border-radius: 999px; background: transparent; display: flex; align-items: center; justify-content: center; cursor: pointer; color: {T["muted"]};">{ico("x", 12, T["muted"])}</button></span>'
        for it in items)
    return (f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px; min-height: 48px; padding: 6px 6px 6px 10px; border: 1px solid {T["border"]}; border-radius: 10px; background: {T["surface"]};">{cs}'
            f'<input id="{id_}" type="text" placeholder="{placeholder}" style="flex-grow: 1; min-width: 80px; border: 0; background: transparent; font-size: 15px; color: {T["ink"]}; outline: none; padding: 6px 4px;">'
            f'<button type="button" aria-label="Add" style="width: 34px; height: 34px; border: 1px dashed {T["border"]}; border-radius: 999px; background: transparent; display: flex; align-items: center; justify-content: center; cursor: pointer; color: {T["muted"]};">{ico("plus", 14, T["muted"])}</button></div>')

def presets(L, T, active=1):
    opts = [("€30 · 1 · 5d", "30 € · 1 · 5d"), ("€40 · 2 · 5d", "40 € · 2 · 5d"), ("€60 · 2 · 7d", "60 € · 2 · 7d")]
    out = []
    for i, (en, es) in enumerate(opts):
        on = i == active
        out.append(f'<button type="button" aria-pressed="{str(on).lower()}" style="min-height: 36px; padding: 0 12px; border: 1px solid {T["green"] if on else T["border"]}; border-radius: 999px; background: {T["greenBg"] if on else T["surface"]}; color: {T["greenInk"] if on else T["ink"]}; font-family: {MONO}; font-size: 13px; cursor: pointer;">{en if L["lang"] == "en" else es}</button>')
    return f'<div style="display: flex; flex-direction: column; gap: 8px;">{label(L["presets"], T)}<div style="display: flex; flex-wrap: wrap; gap: 6px;">{"".join(out)}</div></div>'

def form(L, T, values=None, dim=False, preset=1):
    v = dict(budget="40", people="2", days="5", breakfast=False, lunch=True, dinner=True, diet=0,
             allergies=["nuts" if L["lang"] == "en" else "frutos secos"],
             home=["olive oil", "salt", "rice 500 g"] if L["lang"] == "en" else ["aceite de oliva", "sal", "arroz 500 g"],
             avoid=["mushrooms" if L["lang"] == "en" else "champiñones"],
             note="Tiny kitchen, one pan, no oven." if L["lang"] == "en" else "Cocina pequeña, una sartén, sin horno.")
    if values: v.update(values)
    nmeals = int(v["people"]) * int(v["days"]) * (int(v["breakfast"]) + int(v["lunch"]) + int(v["dinner"]))
    pm = float(v["budget"]) / max(nmeals, 1)
    hint = (L["hintLow"] if pm < 0.85 else L["hint"]).format(pm=eur(pm, L), n=nmeals)
    op = f"opacity: {T['dim']}; pointer-events: none;" if dim else ""
    return f'''<form aria-label="{L['yourWeek']}" style="display: flex; flex-direction: column; gap: 22px; {op}">
  <h2 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 28px; line-height: 1.1; color: {T['ink']};">{L['yourWeek']}</h2>
  {presets(L, T, preset)}
  {field(L['budget'], inp('budget', v['budget'], T, prefix='€', type_='number'), T, 'budget', hint)}
  <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;">
    {field(L['people'], stepper('people', v['people'], T), T, 'people')}
    {field(L['days'], stepper('days', v['days'], T), T, 'days')}
  </div>
  {field(L['meals'], '<div style="display: flex; gap: 8px; flex-wrap: wrap;">' + checkchip('m-b', L['breakfast'], v['breakfast'], T) + checkchip('m-l', L['lunch'], v['lunch'], T) + checkchip('m-d', L['dinner'], v['dinner'], T) + '</div>', T)}
  {field(L['diet'], segmented(L['diets'], v['diet'], T), T)}
  {field(L['allergies'], chips('allergies', v['allergies'], L['allergiesPh'], T), T, 'allergies')}
  {field(L['home'], chips('home', v['home'], L['homePh'], T), T, 'home')}
  {field(L['avoid'], chips('avoid', v['avoid'], L['avoidPh'], T), T, 'avoid')}
  {field(L['note'], f'<textarea id="note" rows="3" placeholder="{L["notePh"]}" style="width: 100%; box-sizing: border-box; padding: 12px 14px; border: 1px solid {T["border"]}; border-radius: 10px; background: {T["surface"]}; font-size: 16px; color: {T["ink"]}; resize: vertical; outline: none;">{v["note"]}</textarea>', T, 'note')}
  <button type="submit" style="min-height: 56px; border: 0; border-radius: 12px; background: {T['green']}; color: {T['onGreen']}; font-family: {SERIF}; font-size: 20px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px;">{L['submit']} {ico('arrowR', 20, T['onGreen'])}</button>
  <p style="margin: 0; font-size: 13px; line-height: 1.5; color: {T['muted']};">{L['fine']}</p>
</form>
'''

def who_badge(kind, L, T):
    txt = L["who"][kind]
    if kind == "ai": bg, fg, bd = T["amberBg"], T["amber"], T["amber"]
    elif kind == "code": bg, fg, bd = T["greenBg"], T["greenInk"], T["green"]
    else: bg, fg, bd = T["surface2"], T["ink"], T["border"]
    return f'<span style="display: inline-flex; align-items: center; min-width: 52px; justify-content: center; padding: 3px 10px; border-radius: 999px; border: 1px solid {bd}; background: {bg}; color: {fg}; font-size: 12px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; font-family: {MONO};">{txt}</span>'

def hero(L, T, mobile=False):
    W, H = (358, 230) if mobile else (760, 320)
    svg = braid_svg(W, H, HERO_STRANDS, 5, T, L=L, uid="h")
    pad = "16px 16px 20px 16px" if mobile else "20px 20px 28px 20px"
    hs = "26px" if mobile else "34px"
    return f'''<section style="display: flex; flex-direction: column; gap: 14px; padding: {pad}; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="border-radius: 10px; background: {T['bg']}; border: 1px solid {T['border']}; overflow: hidden;">{svg}</div>
  <div style="display: flex; flex-direction: column; gap: 6px; padding: 0 4px;">
    <h2 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-style: italic; font-size: {hs}; line-height: 1.1; letter-spacing: -0.01em; color: {T['ink']};">{L['heroTitle']}</h2>
    <p style="margin: 0; font-size: 15px; line-height: 1.5; color: {T['muted']};">{L['heroSub']}</p>
  </div>
</section>
'''

def how_panel(L, T, mobile=False):
    rows = []
    for i, (kind, t, sub) in enumerate(L["steps"]):
        subhtml = f'<div style="font-size: 14px; color: {T["muted"]}; line-height: 1.45;">{sub}</div>' if sub else ""
        rows.append(f'''<li style="display: flex; gap: 14px; align-items: flex-start; padding: 16px 0; border-top: 1px solid {T['border']};">
      <div style="font-family: {SERIF}; font-size: 22px; font-weight: 600; color: {T['muted']}; width: 24px; flex-shrink: 0; line-height: 1.2;">{i+1}</div>
      <div style="display: flex; flex-direction: column; gap: 4px; flex-grow: 1;">
        <div style="font-size: 17px; font-weight: 600; line-height: 1.35; color: {T['ink']};">{t}</div>
        {subhtml}
      </div>
      {who_badge(kind, L, T)}
    </li>''')
    pad = "24px 18px" if mobile else "32px 36px"
    hs = "28px" if mobile else "34px"
    return f'''<section style="display: flex; flex-direction: column; gap: 18px; padding: {pad}; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="display: flex; flex-direction: column; gap: 6px;">
    <h2 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: {hs}; line-height: 1.1; color: {T['ink']};">{L['how']}</h2>
    <p style="margin: 0; font-size: 16px; color: {T['muted']};">{L['howSub']}</p>
  </div>
  <ol style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column;">{"".join(rows)}</ol>
  <div style="display: flex; flex-direction: column; gap: 6px; padding: 18px 20px; border-radius: 12px; background: {T['greenBg']}; border: 1px solid {T['greenSoft']};">
    <div style="font-family: {SERIF}; font-size: 20px; font-weight: 600; font-style: italic; color: {T['greenInk']};">{L['promise']}</div>
    <p style="margin: 0; font-size: 15px; line-height: 1.5; color: {T['ink']};">{L['promiseBody']}</p>
  </div>
</section>
'''

def loading_panel(L, T):
    rows = []
    for st, txt in L["loadSteps"]:
        if st == "done":
            mark = f'<span style="width: 24px; height: 24px; border-radius: 999px; background: {T["green"]}; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{ico("check", 14, T["onGreen"], 3)}</span>'; col = T["muted"]
        elif st == "active":
            mark = f'<span style="width: 24px; height: 24px; border-radius: 999px; border: 3px solid {T["green"]}; border-right-color: {T["greenSoft"]}; box-sizing: border-box; flex-shrink: 0;"></span>'; col = T["ink"]
        else:
            mark = f'<span style="width: 24px; height: 24px; border-radius: 999px; border: 1px solid {T["border"]}; box-sizing: border-box; flex-shrink: 0;"></span>'; col = T["muted"]
        rows.append(f'<li style="display: flex; align-items: center; gap: 14px; font-size: 17px; font-weight: {"600" if st == "active" else "400"}; color: {col}; padding: 9px 0;">{mark}{txt}</li>')
    svg = braid_svg(760, 300, HERO_STRANDS, 5, T, L=L, progress=0.56, uid="ld")
    return f'''<section aria-busy="true" style="display: flex; flex-direction: column; gap: 24px; padding: 36px 40px; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="display: flex; flex-direction: column; gap: 8px;">
    <h2 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 38px; line-height: 1.1; color: {T['ink']};">{L['loadingTitle']}</h2>
    <p style="margin: 0; font-size: 16px; color: {T['muted']};">{L['loadingSub']}</p>
  </div>
  <div style="display: flex; flex-direction: column; gap: 8px;">
    <div style="border-radius: 10px; background: {T['bg']}; border: 1px solid {T['border']}; overflow: hidden;">{svg}</div>
    <div style="display: flex; justify-content: space-between; font-family: {MONO}; font-size: 13px; color: {T['muted']};"><span>{L['loadDay']}</span><span style="display: flex; align-items: center; gap: 6px;">{ico('clock', 14, T['muted'])} {L['elapsed']} / 30 s</span></div>
    <div role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="height: 8px; border-radius: 999px; background: {T['surface2']}; overflow: hidden;"><div style="width: 45%; height: 100%; background: {T['green']}; border-radius: 999px;"></div></div>
  </div>
  <ol style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column;">{"".join(rows)}</ol>
  <div style="font-family: {MONO}; font-size: 14px; color: {T['muted']}; padding: 14px 16px; border-radius: 10px; background: {T['surface2']};">{L['loadMsg']}</div>
</section>
'''

def verdict(kind, L, T, total, budget, mobile=False):
    if kind == "within":
        col, bg, bd, lbl, icon = T["greenInk"], T["greenBg"], T["greenSoft"], L["within"], ico("check", 18, T["greenInk"], 3)
        pct = min(100, round(total / budget * 100)); diff_txt = f'{eur(budget - total, L)} {L["left"]}'
        bar = f'<div style="width: {pct}%; height: 100%; background: {T["green"]}; border-radius: 999px;"></div>'
        pcttxt = f'{pct}% {L["of"]} {eur(budget, L)}'
    else:
        col, bg, bd, lbl, icon = T["red"], T["redBg"], T["redSoft"], L["over"], ico("alert", 18, T["red"], 2.4)
        pct = round(budget / total * 100); diff_txt = f'{L["overBy"]} {eur(total - budget, L)}'
        bar = (f'<div style="width: 100%; height: 100%; background: {T["red"]}; border-radius: 999px;"></div>'
               f'<div style="position: absolute; left: {pct}%; top: -5px; width: 2px; height: 20px; background: {T["ink"]};"></div>')
        pcttxt = f'{eur(budget, L)} = {pct}%'
    big = "56px" if mobile else "72px"; pad = "22px 20px" if mobile else "32px 36px"
    return f'''<section aria-label="{lbl}" style="display: flex; flex-direction: column; gap: 18px; padding: {pad}; border-radius: 16px; background: {bg}; border: 1px solid {bd};">
  <div style="display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: {col};">{icon}{lbl}</div>
  <div style="display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;">
    <div style="font-family: {SERIF}; font-size: {big}; font-weight: 600; line-height: 1; letter-spacing: -0.02em; color: {col};">{eur(total, L)}</div>
    <div style="font-size: 18px; color: {T['ink']};">{L['of']} {eur(budget, L)}</div>
  </div>
  <div style="display: flex; flex-direction: column; gap: 8px;">
    <div role="progressbar" aria-valuenow="{round(total)}" aria-valuemin="0" aria-valuemax="{round(budget)}" style="position: relative; height: 10px; border-radius: 999px; background: {T['surface']}; border: 1px solid {bd};">{bar}</div>
    <div style="display: flex; justify-content: space-between; font-family: {MONO}; font-size: 13px; color: {T['ink']};"><span>{pcttxt}</span><span style="font-weight: 500; color: {col};">{diff_txt}</span></div>
  </div>
</section>
'''

def stats(L, T, mobile=False):
    items = [(eur(1.84, L), L["perMeal"], L["perMealSub"]), (eur(4.10, L), L["leftoverVal"], L["leftoverSub"]), ("9 / 14", L["reuse"], L["reuseSub"])]
    cols = "repeat(1, minmax(0, 1fr))" if mobile else "repeat(3, minmax(0, 1fr))"
    cells = "".join(f'''<div style="display: flex; flex-direction: column; gap: 4px; padding: 18px 20px; border: 1px solid {T['border']}; border-radius: 12px; background: {T['surface']};">
    <div style="font-family: {SERIF}; font-size: 30px; font-weight: 600; line-height: 1.1; color: {T['ink']};">{n}</div>
    <div style="font-size: 15px; font-weight: 600; color: {T['ink']};">{t}</div>
    <div style="font-size: 13px; color: {T['muted']}; line-height: 1.4;">{s}</div>
  </div>''' for n, t, s in items)
    return f'<div style="display: grid; grid-template-columns: {cols}; gap: 12px;">{cells}</div>\n'

DAY_COSTS = [7.12, 6.98, 7.60, 8.44, 6.66]

def reuse_map(L, T, mobile=False):
    W, H = (358, 620) if mobile else (760, 640)
    svg = braid_svg(W, H, real_strands(L), 5, T, labels=True, day_costs=DAY_COSTS, L=L, uid="m", scale=0.8 if mobile else 1.0)
    legend = f'''<div style="display: flex; flex-wrap: wrap; gap: 14px 22px; font-size: 13px; color: {T['muted']};">
    <span style="display: inline-flex; align-items: center; gap: 8px;"><span style="width: 12px; height: 12px; border-radius: 999px; border: 2.5px solid {T['green']}; background: {T['bg']}; box-sizing: border-box;"></span>{L['legendKnot']}</span>
    <span style="display: inline-flex; align-items: center; gap: 8px;"><span style="width: 12px; height: 12px; border-radius: 999px; background: {T['amberInk']};"></span>{L['legendBead']}</span>
    <span style="display: inline-flex; align-items: center; gap: 8px;"><span style="width: 22px; height: 0; border-top: 2px dashed {T['green']};"></span>{L['legendDash']}</span>
  </div>'''
    pad = "20px 12px" if mobile else "32px 36px"; hs = "28px" if mobile else "34px"
    return f'''<section style="display: flex; flex-direction: column; gap: 16px; padding: {pad}; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="display: flex; flex-direction: column; gap: 4px; padding: 0 {'8px' if mobile else '0'};">
    <h2 style="margin: 0; font-family: {SERIF}; font-size: {hs}; font-weight: 600; line-height: 1.1; color: {T['ink']};">{L['mapTitle']}</h2>
    <p style="margin: 0; font-size: 15px; color: {T['muted']};">{L['mapSub']}</p>
  </div>
  <div style="border-radius: 10px; background: {T['bg']}; border: 1px solid {T['border']}; overflow: hidden;">{svg}</div>
  <div style="padding: 0 {'8px' if mobile else '0'};">{legend}</div>
</section>
'''

def shelf(L, T, mobile=False):
    def col(title, items, tone):
        bg = T["greenBg"] if tone == "keep" else T["amberBg"]; bd = T["greenSoft"] if tone == "keep" else T["amber"]
        lis = "".join(f'<li style="display: flex; justify-content: space-between; gap: 8px; padding: 7px 0; border-top: 1px solid {T["border"]}; font-size: 15px;"><span>{it.split(" ", 1)[0]}</span><span style="font-family: {MONO}; font-size: 13px; color: {T["muted"]};">{it.split(" ", 1)[1]}</span></li>' for it in items)
        return f'''<div style="display: flex; flex-direction: column; gap: 8px; padding: 16px 18px; border-radius: 12px; background: {bg}; border: 1px solid {bd};">
      {label(title, T)}
      <ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column;">{lis}</ul>
    </div>'''
    cols = "repeat(1, minmax(0, 1fr))" if mobile else "repeat(2, minmax(0, 1fr))"
    pad = "20px 18px" if mobile else "32px 36px"; hs = "28px" if mobile else "34px"
    return f'''<section style="display: flex; flex-direction: column; gap: 16px; padding: {pad}; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="display: flex; flex-direction: column; gap: 4px;">
    <h2 style="margin: 0; font-family: {SERIF}; font-size: {hs}; font-weight: 600; line-height: 1.1; color: {T['ink']};">{L['shelfTitle']}</h2>
    <p style="margin: 0; font-size: 15px; color: {T['muted']};">{L['shelfSub']}</p>
  </div>
  <div style="display: grid; grid-template-columns: {cols}; gap: 12px;">{col(L['keeps'], L['keepsItems'], 'keep')}{col(L['fridge'], L['fridgeItems'], 'soon')}</div>
  <a href="Main.dc.html" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 48px; padding: 0 18px; border: 1px solid {T['green']}; border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 15px; color: {T['greenInk']}; align-self: flex-start; width: {'100%' if mobile else 'auto'}; box-sizing: border-box;">{ico('loop', 16, T['greenInk'])} {L['planNext']}</a>
</section>
'''

MEALS_EN = [
    ("Lentils with rice and red pepper", "35", ["lentils", "rice", "onion", "red pepper"], None, "Day 3"),
    ("Potato omelette, tomato salad", "30", ["eggs", "potatoes", "onion", "tomatoes"], None, None),
    ("Chickpea and spinach stew", "25", ["chickpeas", "onion", "garlic", "tomato sauce"], None, "Day 4"),
    ("Chicken with rice and courgette", "30", ["chicken", "rice", "courgette"], "rice · Day 1", None),
    ("Spaghetti with tuna and tomato", "20", ["spaghetti", "tuna", "tomato sauce"], None, None),
    ("Lentil soup, day-1 leftovers", "15", ["lentils", "carrots"], "lentils · Day 1", None),
    ("Chickpea and tuna salad", "10", ["chickpeas", "tuna", "tomatoes"], "chickpeas · Day 2", None),
    ("Chicken thighs, roast potatoes", "40", ["chicken thighs", "potatoes", "garlic"], "potatoes · Day 1", None),
    ("Spaghetti with courgette and egg", "20", ["spaghetti", "courgette", "eggs"], "courgette · Day 2", None),
    ("Rice with egg and pepper", "15", ["rice", "eggs", "red pepper"], "rice · Day 2", None),
]
MEALS_ES = [
    ("Lentejas con arroz y pimiento rojo", "35", ["lentejas", "arroz", "cebolla", "pimiento rojo"], None, "Día 3"),
    ("Tortilla de patatas, ensalada de tomate", "30", ["huevos", "patatas", "cebolla", "tomates"], None, None),
    ("Potaje de garbanzos con espinacas", "25", ["garbanzos", "cebolla", "ajo", "tomate frito"], None, "Día 4"),
    ("Pollo con arroz y calabacín", "30", ["pollo", "arroz", "calabacín"], "arroz · Día 1", None),
    ("Espaguetis con atún y tomate", "20", ["espaguetis", "atún", "tomate frito"], None, None),
    ("Sopa de lentejas, sobras del día 1", "15", ["lentejas", "zanahorias"], "lentejas · Día 1", None),
    ("Ensalada de garbanzos y atún", "10", ["garbanzos", "atún", "tomates"], "garbanzos · Día 2", None),
    ("Muslos de pollo con patatas asadas", "40", ["muslos de pollo", "patatas", "ajo"], "patatas · Día 1", None),
    ("Espaguetis con calabacín y huevo", "20", ["espaguetis", "calabacín", "huevos"], "calabacín · Día 2", None),
    ("Arroz con huevo y pimiento", "15", ["arroz", "huevos", "pimiento rojo"], "arroz · Día 2", None),
]
RECIPE_EN = dict(ing=["Lentils 250 g", "Rice 200 g", "1 onion", "1 red pepper", "2 tbsp olive oil (home)", "Salt (home)"],
                 steps=["Soften the chopped onion and pepper in oil, 6 min.", "Add lentils and 900 ml water. Simmer 25 min.", "Cook the rice separately, 12 min. Serve the lentils over it.", "Keep half the lentils for Day 3's soup."])
RECIPE_ES = dict(ing=["Lentejas 250 g", "Arroz 200 g", "1 cebolla", "1 pimiento rojo", "2 cdas aceite de oliva (casa)", "Sal (casa)"],
                 steps=["Pocha la cebolla y el pimiento picados en aceite, 6 min.", "Añade las lentejas y 900 ml de agua. Cuece 25 min.", "Cuece el arroz aparte, 12 min. Sirve las lentejas encima.", "Guarda la mitad de las lentejas para la sopa del día 3."])

def pill(text, T, kind="use"):
    if kind == "reuse":
        return f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 6px; background: {T["greenBg"]}; color: {T["greenInk"]}; font-size: 12px; font-weight: 600; font-family: {MONO};">{ico("loop", 11, T["greenInk"], 2.2)} {text}</span>'
    if kind == "left":
        return f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 6px; background: {T["amberBg"]}; color: {T["amber"]}; font-size: 12px; font-weight: 600; font-family: {MONO};">{text}</span>'
    return f'<span style="padding: 2px 8px; border-radius: 6px; background: {T["surface2"]}; color: {T["muted"]}; font-size: 12px; font-family: {MONO};">{text}</span>'

def meal_row(kind, m, L, T, expanded, mobile):
    name, mins, uses, reused, leftover = m
    R = RECIPE_EN if L["lang"] == "en" else RECIPE_ES
    pills = "".join(pill(u, T) for u in uses)
    if reused: pills += pill(f'{L["reusedFrom"]} {reused}', T, "reuse")
    if leftover: pills += pill(f'{L["leftoverTo"]} {leftover}', T, "left")
    chev = ico("chevD" if expanded else "chevR", 16, T["muted"])
    body = ""
    if expanded:
        ings = "".join(f'<li style="padding: 3px 0;">{i}</li>' for i in R["ing"])
        steps = "".join(f'<li style="padding: 3px 0 3px 4px;">{s}</li>' for s in R["steps"])
        cols = "repeat(1, minmax(0, 1fr))" if mobile else "220px minmax(0, 1fr)"
        body = f'''<div style="display: grid; grid-template-columns: {cols}; gap: 20px; padding: 6px 0 14px 0; font-size: 15px; line-height: 1.5; color: {T['ink']};">
        <div style="display: flex; flex-direction: column; gap: 6px;">{label(L['ingredients'], T)}<ul style="margin: 0; padding: 0 0 0 18px;">{ings}</ul></div>
        <div style="display: flex; flex-direction: column; gap: 6px;">{label(L['method'], T)}<ol style="margin: 0; padding: 0 0 0 18px;">{steps}</ol></div>
      </div>'''
    return f'''<div style="display: flex; flex-direction: column; border-top: 1px solid {T['border']};">
      <button type="button" aria-expanded="{str(expanded).lower()}" style="display: flex; align-items: flex-start; gap: 12px; width: 100%; min-height: 56px; padding: 12px 0; border: 0; background: transparent; text-align: left; cursor: pointer; color: {T['ink']};">
        <span style="width: {'52px' if mobile else '64px'}; flex-shrink: 0; font-size: 12px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {T['muted']}; padding-top: 4px;">{kind}</span>
        <span style="display: flex; flex-direction: column; gap: 6px; flex-grow: 1; min-width: 0;">
          <span style="font-family: {SERIF}; font-size: {'18px' if mobile else '20px'}; font-weight: 600; line-height: 1.2;">{name} <span style="font-family: {MONO}; font-size: 12px; font-weight: 400; color: {T['muted']};">{mins} {L['min']}</span></span>
          <span style="display: flex; flex-wrap: wrap; gap: 6px;">{pills}</span>
        </span>
        <span style="padding-top: 6px;">{chev}</span>
      </button>
      {body}
    </div>'''

def plan(L, T, mobile=False):
    MEALS = MEALS_EN if L["lang"] == "en" else MEALS_ES
    days = []
    for d in range(5):
        rows = meal_row(L["lunchL"], MEALS[d*2], L, T, d == 0, mobile) + meal_row(L["dinnerL"], MEALS[d*2+1], L, T, False, mobile)
        days.append(f'''<article style="display: flex; flex-direction: column; padding: 0 0 8px 0;">
    <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 18px 0 8px 0;">
      <h3 style="margin: 0; font-family: {SERIF}; font-size: 24px; font-weight: 600; font-style: italic; color: {T['ink']};">{L['day']} {d+1} <span style="font-style: normal; font-size: 15px; font-family: {SANS}; font-weight: 400; color: {T['muted']};">· {L['dayNames'][d]}</span></h3>
      <span style="font-family: {MONO}; font-size: 13px; color: {T['muted']};">{eur(DAY_COSTS[d], L)}</span>
    </div>
    {rows}
  </article>''')
    pad = "20px 18px" if mobile else "32px 36px"; hs = "28px" if mobile else "34px"
    return f'''<section style="display: flex; flex-direction: column; padding: {pad}; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="display: flex; flex-direction: column; gap: 4px; padding-bottom: 8px;">
    <h2 style="margin: 0; font-family: {SERIF}; font-size: {hs}; font-weight: 600; line-height: 1.1; color: {T['ink']};">{L['planTitle']}</h2>
    <p style="margin: 0; font-size: 15px; color: {T['muted']};">{L['planSub']}</p>
  </div>
  {"".join(days)}
</section>
'''

ITEMS_EN = [
    (0, "Onions, net 1 kg", "600 g", "1", "400 g", 1.35, False), (0, "Potatoes, bag 3 kg", "1.8 kg", "1", "1.2 kg", 2.99, False),
    (0, "Red pepper, each", "2", "2", "—", 1.58, False), (0, "Tomatoes, bag 1 kg", "700 g", "1", "300 g", 1.89, False),
    (0, "Courgette, 1 kg", "600 g", "1", "400 g", 1.79, False), (0, "Carrots, bag 1 kg", "300 g", "1", "700 g", 0.99, False),
    (0, "Garlic, net 3", "4 cloves", "1", "2 heads", 0.89, False), (0, "Apples, 1 kg", "1 kg", "1", "—", 1.94, False),
    (1, "Chicken breast, tray 650 g", "600 g", "1", "50 g", 4.35, False), (1, "Chicken thighs, tray 1 kg", "1 kg", "1", "—", 3.79, False),
    (2, "Eggs L, box 12", "10", "1", "2", 2.65, False), (2, "Grated cheese, 200 g", "150 g", "1", "50 g", 1.55, False),
    (2, "Natural yoghurt, 4 × 125 g", "4", "1", "—", 1.20, False),
    (3, "Round rice, bag 1 kg", "800 g", "1 (+500 g home)", "700 g", 1.19, False), (3, "Lentils, bag 1 kg", "500 g", "1", "500 g", 1.45, False),
    (3, "Cooked chickpeas, jar 400 g", "2 jars", "2", "—", 1.30, False), (3, "Spaghetti, 1 kg", "500 g", "1", "500 g", 1.10, False),
    (4, "Tomato sauce, brick 400 g", "2", "2", "—", 1.30, False), (4, "Tuna in oil, 3 × 80 g", "2 tins", "1 pack", "1 tin", 2.35, False),
    (4, "Sliced bread, 460 g", "1", "1", "—", 1.15, False), (4, "Olive oil", "150 ml", "—", "—", 0.00, True), (4, "Salt", "—", "—", "—", 0.00, True),
]
ITEMS_ES = [
    (0, "Cebollas, malla 1 kg", "600 g", "1", "400 g", 1.35, False), (0, "Patatas, bolsa 3 kg", "1,8 kg", "1", "1,2 kg", 2.99, False),
    (0, "Pimiento rojo, ud", "2", "2", "—", 1.58, False), (0, "Tomates, bolsa 1 kg", "700 g", "1", "300 g", 1.89, False),
    (0, "Calabacín, 1 kg", "600 g", "1", "400 g", 1.79, False), (0, "Zanahorias, bolsa 1 kg", "300 g", "1", "700 g", 0.99, False),
    (0, "Ajos, malla 3", "4 dientes", "1", "2 cabezas", 0.89, False), (0, "Manzanas, 1 kg", "1 kg", "1", "—", 1.94, False),
    (1, "Pechuga de pollo, bandeja 650 g", "600 g", "1", "50 g", 4.35, False), (1, "Muslos de pollo, bandeja 1 kg", "1 kg", "1", "—", 3.79, False),
    (2, "Huevos L, 12 ud", "10", "1", "2", 2.65, False), (2, "Queso rallado, 200 g", "150 g", "1", "50 g", 1.55, False),
    (2, "Yogur natural, 4 × 125 g", "4", "1", "—", 1.20, False),
    (3, "Arroz redondo, bolsa 1 kg", "800 g", "1 (+500 g casa)", "700 g", 1.19, False), (3, "Lentejas, bolsa 1 kg", "500 g", "1", "500 g", 1.45, False),
    (3, "Garbanzos cocidos, bote 400 g", "2 botes", "2", "—", 1.30, False), (3, "Espaguetis, 1 kg", "500 g", "1", "500 g", 1.10, False),
    (4, "Tomate frito, brik 400 g", "2", "2", "—", 1.30, False), (4, "Atún en aceite, 3 × 80 g", "2 latas", "1 pack", "1 lata", 2.35, False),
    (4, "Pan de molde, 460 g", "1", "1", "—", 1.15, False), (4, "Aceite de oliva", "150 ml", "—", "—", 0.00, True), (4, "Sal", "—", "—", "—", 0.00, True),
]

def receipt_rows(L, T, mobile=False, tick=False):
    ITEMS = ITEMS_EN if L["lang"] == "en" else ITEMS_ES
    tickcol = "22px " if tick else ""
    cols = tickcol + ("minmax(0, 1fr) 52px 44px 52px 52px" if mobile else "minmax(0, 1fr) 96px 110px 84px 72px")
    box = f'<span style="width: 12px; height: 12px; border: 1.5px solid {T["ink"]}; border-radius: 2px; display: inline-block; margin-top: 3px;"></span>' if tick else ""
    rows = []
    for a, aisle in enumerate(L["aisles"]):
        rows.append(f'<div style="padding: 14px 0 6px 0; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: {T["muted"]};">{aisle}</div>')
        for (ai, item, need, buy, left, cost, home) in ITEMS:
            if ai != a: continue
            if home:
                rows.append(f'<div style="display: grid; grid-template-columns: {cols}; gap: 8px; padding: 5px 0; color: {T["muted"]};">{"<span></span>" if tick else ""}<span style="text-decoration: line-through;">{item}</span><span>{need}</span><span style="color: {T["greenInk"]}; font-weight: 500;">{L["atHome"]}</span><span>—</span><span style="text-align: right;">{num(0, L)}</span></div>')
            else:
                ls = f'color: {T["amber"]}; font-weight: 500;' if left != "—" else f'color: {T["muted"]};'
                rows.append(f'<div style="display: grid; grid-template-columns: {cols}; gap: 8px; padding: 5px 0; align-items: baseline;">{box}<span style="color: {T["ink"]}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{item}</span><span style="color: {T["muted"]};">{need}</span><span style="color: {T["ink"]}; font-weight: 500;">{buy}</span><span style="{ls}">{left}</span><span style="text-align: right; color: {T["ink"]};">{num(cost, L)}</span></div>')
    header = f'<div style="display: grid; grid-template-columns: {cols}; gap: 8px; padding: 8px 0; border-top: 2px dashed {T["border"]}; border-bottom: 2px dashed {T["border"]}; font-weight: 500; color: {T["muted"]}; text-transform: uppercase; letter-spacing: 0.04em;">{"<span></span>" if tick else ""}<span>{L["colItem"]}</span><span>{L["colNeed"]}</span><span>{L["colBuy"]}</span><span>{L["colLeft"]}</span><span style="text-align: right;">{L["colCost"]}</span></div>'
    total = round(sum(i[5] for i in ITEMS), 2)
    return header + "".join(rows), total

def receipt_totals(L, T, total, budget):
    over = total > budget; diff = abs(budget - total)
    return f'''<div style="margin-top: 12px; padding-top: 12px; border-top: 2px dashed {T['border']}; display: flex; flex-direction: column; gap: 6px;">
      <div style="display: flex; justify-content: space-between; font-weight: 500; font-size: 16px; color: {T['ink']};"><span>{L['subtotal']}</span><span>{eur(total, L)}</span></div>
      <div style="display: flex; justify-content: space-between; color: {T['muted']};"><span>{L['budgetL']}</span><span>{eur(budget, L)}</span></div>
      <div style="display: flex; justify-content: space-between; font-weight: 500; color: {T['red'] if over else T['greenInk']};"><span>{L['overL'] if over else L['remaining']}</span><span>{eur(diff, L)}</span></div>
    </div>'''

def receipt(L, T, budget, mobile=False):
    rows, total = receipt_rows(L, T, mobile)
    btn = f'display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 16px; border: 1px solid {T["border"]}; border-radius: 10px; background: {T["surface"]}; color: {T["ink"]}; font-size: 14px; font-weight: 600; cursor: pointer; font-family: {SANS};'
    pad = "20px 14px" if mobile else "32px 36px"; hs = "28px" if mobile else "34px"
    return f'''<section style="display: flex; flex-direction: column; gap: 18px; padding: {pad}; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">
  <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
    <div style="display: flex; flex-direction: column; gap: 4px;">
      <h2 style="margin: 0; font-family: {SERIF}; font-size: {hs}; font-weight: 600; line-height: 1.1; color: {T['ink']};">{L['receiptTitle']}</h2>
      <p style="margin: 0; font-size: 15px; color: {T['muted']};">{L['receiptSub']} · {L['itemsCount']}</p>
    </div>
    <div style="display: flex; gap: 8px;">
      <button type="button" style="{btn}">{ico('copy', 16, T['ink'])} {L['copy']}</button>
      <a href="PrintReceipt.dc.html" style="{btn} text-decoration: none;">{ico('print', 16, T['ink'])} {L['print']}</a>
    </div>
  </div>
  <div style="font-family: {MONO}; font-size: {'12px' if mobile else '13.5px'}; line-height: 1.4; background: {T['bg']}; border: 1px solid {T['border']}; border-radius: 4px; padding: 20px {'12px' if mobile else '24px'}; display: flex; flex-direction: column;">
    <div style="text-align: center; font-weight: 500; letter-spacing: 0.14em; padding-bottom: 4px; color: {T['ink']};">MERCADONA</div>
    <div style="text-align: center; color: {T['muted']}; padding-bottom: 14px;">{L['receiptSub'].split(' · ')[0].upper()} · 22/09/2026</div>
    {rows}
    {receipt_totals(L, T, total, budget)}
    <div style="text-align: center; color: {T['muted']}; padding-top: 16px; letter-spacing: 0.06em;">{L['recipes'].upper()}</div>
  </div>
</section>
'''

def changes_card(L, T, mobile=False):
    rows = []
    for t, s, sub in L["changes"]:
        rows.append(f'''<li style="display: flex; align-items: center; gap: 14px; padding: 16px 0; border-top: 1px solid {T['redSoft']}; flex-wrap: {'wrap' if mobile else 'nowrap'};">
      <div style="display: flex; flex-direction: column; gap: 3px; flex-grow: 1; min-width: {'100%' if mobile else '0'};">
        <div style="font-size: 17px; font-weight: 600; color: {T['ink']};">{t}</div>
        <div style="font-size: 14px; color: {T['muted']};">{sub}</div>
      </div>
      <div style="font-family: {MONO}; font-size: 18px; font-weight: 500; color: {T['greenInk']}; flex-shrink: 0; {'flex-grow: 1;' if mobile else ''}">{s}</div>
      <button type="button" style="min-height: 44px; padding: 0 16px; border: 1px solid {T['border']}; border-radius: 10px; background: {T['surface']}; color: {T['ink']}; font-size: 14px; font-weight: 600; cursor: pointer; flex-shrink: 0;">{L['apply']}</button>
    </li>''')
    pad = "20px 18px" if mobile else "28px 36px"; hs = "26px" if mobile else "30px"
    return f'''<section style="display: flex; flex-direction: column; gap: 6px; padding: {pad}; border: 1px solid {T['redSoft']}; border-radius: 16px; background: {T['surface']};">
  <h2 style="margin: 0; font-family: {SERIF}; font-size: {hs}; font-weight: 600; line-height: 1.1; color: {T['ink']};">{L['changeTitle']}</h2>
  <p style="margin: 0 0 12px 0; font-size: 15px; color: {T['muted']};">{L['changeSub']}</p>
  <ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column;">{"".join(rows)}</ul>
</section>
'''

def not_realistic(L, T, mobile=False):
    reasons = "".join(f'<li style="display: flex; gap: 12px; padding: 8px 0; font-size: 16px; line-height: 1.5; color: {T["ink"]};"><span style="font-family: {MONO}; color: {T["red"]}; flex-shrink: 0;">{i+1}.</span><span>{r}</span></li>' for i, r in enumerate(L["nrReasons"]))
    opts = "".join(f'''<button type="button" style="display: flex; flex-direction: column; align-items: flex-start; gap: 4px; padding: 18px 20px; border: 1px solid {T['border']}; border-radius: 12px; background: {T['surface']}; text-align: left; cursor: pointer; color: {T['ink']};">
      <span style="font-family: {SERIF}; font-size: 20px; font-weight: 600; line-height: 1.2;">{t}</span>
      <span style="font-size: 14px; color: {T['muted']};">{s}</span>
    </button>''' for t, s in L["nrOpts"])
    pad = "22px 18px" if mobile else "32px 36px"; hs = "34px" if mobile else "44px"
    cols = "repeat(1, minmax(0, 1fr))" if mobile else "repeat(2, minmax(0, 1fr))"
    return f'''<section aria-label="{L['notreal']}" style="display: flex; flex-direction: column; gap: 18px; padding: {pad}; border-radius: 16px; background: {T['surface']}; border: 1px solid {T['redSoft']};">
  <div style="display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: {T['red']};">{ico('alert', 18, T['red'], 2.4)}{L['notreal']}</div>
  <h2 style="margin: 0; font-family: {SERIF}; font-size: {hs}; font-weight: 600; line-height: 1.05; letter-spacing: -0.01em; color: {T['ink']};">{L['nrTitle']}</h2>
  <p style="margin: 0; font-size: 17px; line-height: 1.5; color: {T['ink']};">{L['nrSub']}</p>
  <div style="display: flex; align-items: baseline; gap: 12px; padding: 16px 20px; border-radius: 12px; background: {T['redBg']}; flex-wrap: wrap;">
    <span style="font-family: {SERIF}; font-size: 40px; font-weight: 600; color: {T['red']}; line-height: 1;">{eur(0.29, L)}</span>
    <span style="font-size: 15px; color: {T['ink']};">{L['perMeal']} · 42 {L['mealsWord']}</span>
  </div>
</section>
<section style="display: flex; flex-direction: column; gap: 8px; padding: {pad}; border-radius: 16px; background: {T['surface']}; border: 1px solid {T['border']};">
  {label(L['nrWhy'], T)}
  <ol style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column;">{reasons}</ol>
</section>
<section style="display: flex; flex-direction: column; gap: 14px;">
  <h3 style="margin: 0; font-family: {SERIF}; font-size: 28px; font-weight: 600; color: {T['ink']};">{L['nrTry']}</h3>
  <div style="display: grid; grid-template-columns: {cols}; gap: 12px;">{opts}</div>
  <p style="margin: 0; font-size: 14px; color: {T['muted']}; line-height: 1.5;">{L['nrNo']}</p>
</section>
'''

def summary_bar(L, T, txt):
    return f'''<a href="Main.dc.html" style="display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 48px; padding: 0 14px; border: 1px solid {T['border']}; border-radius: 10px; background: {T['surface']}; text-decoration: none; color: {T['ink']};">
  <span style="display: inline-flex; align-items: center; gap: 8px; font-family: {MONO}; font-size: 13px;">{ico('chevL', 14, T['muted'])} {txt}</span>
  <span style="display: inline-flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: {T['greenInk']};">{ico('edit', 14, T['greenInk'])} {L['edit']}</span>
</a>'''

# ---------- screens ----------
def desktop(title, L, T, dark, left_html, right_html, h):
    w = 1280
    return (head(title, L, T, w, h) + topbar(L, T, False, dark) +
            f'''<main style="display: grid; grid-template-columns: 420px minmax(0, 1fr); gap: 40px; padding: 36px 48px 48px 48px; align-items: start; flex-grow: 1;">
  <aside style="display: flex; flex-direction: column; gap: 24px; padding: 28px; border: 1px solid {T['border']}; border-radius: 16px; background: {T['surface']};">{left_html}</aside>
  <div style="display: flex; flex-direction: column; gap: 20px; min-width: 0;">{right_html}</div>
</main>
''' + tail(w, h))

def mobile(title, L, T, dark, body_html, h):
    w = 390
    return (head(title, L, T, w, h) + topbar(L, T, True, dark) +
            f'<main style="display: flex; flex-direction: column; gap: 16px; padding: 16px 16px 40px 16px; flex-grow: 1;">{body_html}</main>\n' + tail(w, h))

def result_within(L, T, m=False):
    return verdict("within", L, T, 36.80, 40.00, m) + stats(L, T, m) + reuse_map(L, T, m) + shelf(L, T, m) + plan(L, T, m) + receipt(L, T, 40.00, m)

def result_over(L, T, m=False):
    return (verdict("over", L, T, 36.80, 30.00, m) + f'<p style="margin: 0; font-size: 15px; color: {T["muted"]};">{L["overHint"]}</p>' +
            changes_card(L, T, m) + stats(L, T, m) + reuse_map(L, T, m) + plan(L, T, m) + receipt(L, T, 30.00, m))

def print_receipt(L):
    T = PRINT
    rows, total = receipt_rows(L, T, False, tick=True)
    w, h = 794, 1123
    return (head("Print — shopping list", L, T, w, h) + f'''<div style="display: flex; flex-direction: column; gap: 18px; padding: 56px 60px; font-family: {MONO}; font-size: 12.5px; line-height: 1.4; color: {T['ink']};">
  <div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid {T['ink']}; padding-bottom: 12px;">
    <div style="display: flex; flex-direction: column; gap: 2px;">
      <div style="font-family: {SERIF}; font-size: 26px; font-style: italic; font-weight: 600;">{L['app']}</div>
      <div style="color: {T['muted']};">{L['receiptTitle']} · {L['receiptSub']} · 22/09/2026</div>
    </div>
    <div style="text-align: right; color: {T['muted']};">{L['printFor']}: 2 · 5 {L['days'].lower()} · {L['lunchL']} + {L['dinnerL']}<br>{L['printTick']}</div>
  </div>
  {rows}
  {receipt_totals(L, T, total, 40.00)}
  <div style="display: flex; justify-content: space-between; color: {T['muted']}; padding-top: 12px; border-top: 1px solid {T['border']}; letter-spacing: 0.06em;"><span>{L['recipes'].upper()}</span><span>{L['itemsCount'].upper()}</span></div>
</div>
''' + tail(w, h))

boards = {}
def add(name, html, w, h, x, y, title=None, extra=None):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(html)
    e = dict(x=x, y=y, w=w, h=h)
    if title: e["title"] = title
    if extra: e.update(extra)
    boards[name] = e

T, D = LIGHT, DARK
# Row 1 — desktop light EN
H1, H2, H3, H4, H5 = 1560, 1560, 4560, 4640, 1560
add("Main.dc.html", desktop("Empty state", EN, T, False, form(EN, T), hero(EN, T) + how_panel(EN, T), H1), 1280, H1, 0, 0, "1 · Empty state")
add("Loading.dc.html", desktop("Loading", EN, T, False, form(EN, T, dim=True), loading_panel(EN, T), H2), 1280, H2, 1360, 0, "2 · Loading")
add("WithinBudget.dc.html", desktop("Within budget", EN, T, False, form(EN, T), result_within(EN, T), H3), 1280, H3, 2720, 0, "3 · Within budget")
add("OverBudget.dc.html", desktop("Over budget", EN, T, False, form(EN, T, values=dict(budget="30"), preset=-1), result_over(EN, T), H4), 1280, H4, 4080, 0, "4 · Over budget")
NR_VALUES = dict(budget="12", days="7", breakfast=True, home=[], allergies=[], avoid=[], note="")
add("NotRealistic.dc.html", desktop("Not realistic", EN, T, False, form(EN, T, values=NR_VALUES, preset=-1), not_realistic(EN, T), H5), 1280, H5, 5440, 0, "5 · Not realistic")

# Row 2 — mobile light EN
Y2 = H4 + 120 + 223
M1, M2, M3, M4 = 2760, 6300, 6600, 1500
add("MobileEmpty.dc.html", mobile("Empty state (mobile)", EN, T, False,
    hero(EN, T, True) + f'<div style="display: flex; flex-direction: column; gap: 22px; padding: 22px 16px; border: 1px solid {T["border"]}; border-radius: 16px; background: {T["surface"]};">{form(EN, T)}</div>' + how_panel(EN, T, True), M1), 390, M1, 0, Y2, "6a · Mobile empty")
add("MobileWithin.dc.html", mobile("Within budget (mobile)", EN, T, False, summary_bar(EN, T, "€40 · 2 · 5d · lunch + dinner") + result_within(EN, T, True), M2), 390, M2, 470, Y2, "6b · Mobile within budget")
add("MobileOver.dc.html", mobile("Over budget (mobile)", EN, T, False, summary_bar(EN, T, "€30 · 2 · 5d · lunch + dinner") + result_over(EN, T, True), M3), 390, M3, 940, Y2, "6c · Mobile over budget")
add("MobileNotRealistic.dc.html", mobile("Not realistic (mobile)", EN, T, False, summary_bar(EN, T, "€12 · 2 · 7d · 3 meals") + not_realistic(EN, T, True), M4), 390, M4, 1410, Y2, "6d · Mobile not realistic")

# Row 3 — dark mode · Español · print
Y3 = Y2 + M3 + 120 + 223
add("DarkWithinES.dc.html", desktop("Dentro del presupuesto (oscuro)", ES, D, True, form(ES, D), result_within(ES, D), H3), 1280, H3, 0, Y3, "Dark · ES · Within budget")
add("DarkMobileES.dc.html", mobile("Dentro del presupuesto (móvil, oscuro)", ES, D, True, summary_bar(ES, D, "40 € · 2 · 5d · comida + cena") + result_within(ES, D, True), M2), 390, M2, 1360, Y3, "Dark · ES · Mobile result")
add("DarkMobileEmptyES.dc.html", mobile("Inicio (móvil, oscuro)", ES, D, True,
    hero(ES, D, True) + f'<div style="display: flex; flex-direction: column; gap: 22px; padding: 22px 16px; border: 1px solid {D["border"]}; border-radius: 16px; background: {D["surface"]};">{form(ES, D)}</div>' + how_panel(ES, D, True), M1), 390, M1, 1830, Y3, "Dark · ES · Mobile empty")
add("PrintReceipt.dc.html", print_receipt(EN), 794, 1123, 2300, Y3, "Print · A4 receipt", extra={"paper": "a4", "print": "flow"})

order = list(boards.keys())
now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
canvas = {
    "v": 3, "createdOnFiles": {"v": 1, "at": now}, "title": "Student Meal Planner",
    "launch": {"view": "canvas"}, "pages": [], "boards": boards, "order": order,
    "notes": {
        "t1": {"x": 0, "y": -300, "text": "Desktop · light · EN — form left, results right", "kind": "title1", "maxW": 6720},
        "t2": {"x": 0, "y": Y2 - 300, "text": "Mobile · light · EN — 390 wide", "kind": "title1", "maxW": 1800},
        "t3": {"x": 0, "y": Y3 - 300, "text": "Dark mode · Español · Print", "kind": "title1", "maxW": 3100},
        "s1": {"x": 1900, "y": Y2 + 40, "w": 340, "text": "Threaded Pantry: the braid in the hero, the loading frame and the reuse map is one seeded algorithm. Strand = ingredient, knot = cooked that day, amber bead = leftover, dashed lead-in = already at home. Same seed, same drawing.", "fill": "green"},
        "s2": {"x": 1900, "y": Y2 + 400, "w": 340, "text": "Form: quick-start presets, and a live hint under the budget that turns into a warning below the €0.85 per-meal floor — so 'not realistic' is visible before you submit.", "fill": "orange"},
    },
    "designSystems": [],
}
with open(os.path.join(ROOT, "canvas.json"), "w", encoding="utf-8") as f:
    json.dump(canvas, f, indent=1, ensure_ascii=False)
print("ok", len(boards))
