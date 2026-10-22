import re
import unicodedata
import pandas as pd
from rapidfuzz.fuzz import partial_ratio

CATEGORIAS = {
    "carga laboral": ["carga", "sobrecarga", "mucho trabajo", "muchas tareas", "plazo", "urgente", "para ayer", "no alcanzo", "no doy abasto"],
    "jornada y desconexión": ["horario", "jornada", "turno", "horas extra", "salgo tarde", "muchas horas", "fin de semana", "sin descanso", "sin pausas", "desconectarme"],
    "relaciones y liderazgo": ["trato", "tratan mal", "maltrato", "gritan", "humillan", "insultan", "irrespeto", "burlan", "jefe", "jefa"],
    "apoyo social y liderazgo": ["no me escuchan", "no me apoyan", "ignoran", "no me ayudan", "solo", "sola"],
    "reconocimiento laboral": ["no reconocen", "no valoran", "solo ven mis errores", "sin reconocimiento"],
    "claridad del rol": ["funciones", "no se que hacer", "no esta claro", "cambian mis tareas"],
    "autonomía y control": ["no puedo decidir", "sin autonomia", "todo lo deciden", "me controlan"],
    "seguridad laboral": ["me van a echar", "no me renuevan", "perder el trabajo", "inestabilidad"],
    "relaciones laborales": ["mal ambiente", "conflicto", "peleas", "equipo dividido", "excluyen"],
}

NEGACIONES = ["no tengo", "no ocurre", "no pasa", "nunca me", "ya no"]

def norm(x):
    x = unicodedata.normalize("NFD", str(x).lower().strip())
    x = "".join(c for c in x if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9ñ\s]", " ", x)).strip()

def _negada(texto, frase):
    t, f = norm(texto), norm(frase)
    pos = t.find(f)
    if pos < 0:
        return False
    previo = t[max(0, pos - 18):pos]
    return any(norm(n) in previo for n in NEGACIONES)

def detectar(texto, df):
    t = norm(texto)
    candidatos = []
    for _, r in df.iterrows():
        valores = [str(r.expresion)] + ([] if pd.isna(r.variantes) else str(r.variantes).split("|"))
        puntajes = []
        for valor in valores:
            v = norm(valor)
            score = 100 if v in t else partial_ratio(v, t)
            if not _negada(texto, valor):
                puntajes.append(score)
        mejor = max(puntajes or [0])
        if mejor >= 78:
            candidatos.append({"dimension": str(r.dimension_probable), "pregunta": str(r.pregunta_aclaratoria), "score": mejor, "fuente": "diccionario"})

    for dimension, palabras in CATEGORIAS.items():
        coincidencias = [p for p in palabras if norm(p) in t and not _negada(texto, p)]
        if coincidencias:
            candidatos.append({"dimension": dimension, "pregunta": pregunta_dimension(dimension), "score": 90, "fuente": "categoria"})

    unicos, vistos = [], set()
    for item in sorted(candidatos, key=lambda z: z["score"], reverse=True):
        if item["dimension"] not in vistos:
            unicos.append(item); vistos.add(item["dimension"])
    return unicos[:3]

def pregunta_dimension(dimension):
    return {
        "carga laboral": "¿Qué tareas o plazos están generando mayor presión?",
        "jornada y desconexión": "¿Qué tan extensa suele ser tu jornada y con qué frecuencia ocurre?",
        "relaciones y liderazgo": "¿Qué comportamientos concretos hacen que percibas un trato inadecuado?",
        "apoyo social y liderazgo": "¿Qué apoyo solicitaste y qué respuesta recibiste?",
        "reconocimiento laboral": "¿Qué situaciones te hacen sentir que tu trabajo no es reconocido?",
        "claridad del rol": "¿Qué responsabilidades o expectativas no están claras?",
        "autonomía y control": "¿En qué aspectos no puedes tomar decisiones?",
        "seguridad laboral": "¿Qué hechos aumentaron tu preocupación por la continuidad laboral?",
        "relaciones laborales": "¿Qué situaciones concretas muestran que el ambiente laboral es difícil?",
    }.get(dimension, "¿Puedes contarme un ejemplo concreto?")

def relacion(t):
    t = norm(t)
    if any(x in t for x in ["ambas", "las dos", "trabajo y personal"]): return "ambas"
    if any(x in t for x in ["personal", "familia", "pareja", "fuera del trabajo"]): return "personal"
    if any(x in t for x in ["no se", "no estoy seguro", "no estoy segura", "tal vez"]): return "incierta"
    if any(x in t for x in ["trabajo", "laboral", "jefe", "empresa", "tareas", "turno"]): return "trabajo"

def frecuencia(t):
    t = norm(t); m = re.search(r"(\d+)\s*veces?", t)
    if m:
        n = int(m.group(1)); return "Ocurrió una vez" if n == 1 else ("Sucede casi todos los días" if n >= 4 else "Sucede varias veces por semana")
    mapa = {"Ocurrió una vez":["una vez","solo paso una vez"], "Sucede ocasionalmente":["a veces","de vez en cuando","ocasionalmente"], "Sucede varias veces por semana":["varias veces por semana","cada semana","muy seguido"], "Sucede casi todos los días":["todos los dias","cada dia","diariamente","siempre"]}
    for cat, vals in mapa.items():
        if any(v in t for v in vals): return cat

def duracion(t):
    t = norm(t); m = re.search(r"(\d+)\s*mes", t)
    if m:
        n = int(m.group(1)); return "Más de seis meses" if n >= 6 else ("Algunos meses" if n >= 2 else "Varias semanas")
    mapa = {"Pocos días":["ayer","pocos dias","esta semana"], "Varias semanas":["semanas","un mes"], "Algunos meses":["meses"], "Más de seis meses":["medio año","un año","años","año pasado"]}
    for cat, vals in mapa.items():
        if any(v in t for v in vals): return cat

def impactos(t):
    t = norm(t)
    if any(x in t for x in ["no me afecta", "ninguno", "no ha afectado"]): return ["Ninguno"]
    mapa = {"Descanso":["dormir","sueño","descanso","insomnio"], "Concentración":["concentracion","concentrarme","distraido","no me concentro"], "Motivación":["motivacion","sin ganas","desmotivado"], "Relaciones":["compañeros","equipo","conflictos"], "Vida personal":["familia","pareja","casa","vida personal"], "Tareas":["tareas","entregas","errores","rendimiento"]}
    return [k for k, vals in mapa.items() if any(x in t for x in vals)]

def nivel(f, d, imps):
    fs={"Ocurrió una vez":0,"Sucede ocasionalmente":1,"Sucede varias veces por semana":2,"Sucede casi todos los días":3}; ds={"Pocos días":0,"Varias semanas":1,"Algunos meses":2,"Más de seis meses":3}
    p=fs.get(f,0)+ds.get(d,0)+min(len([x for x in imps if x!="Ninguno"]),2)
    return "Situación laboral puntual" if p<=1 else ("Posible factor psicosocial recurrente" if p<=4 else "Revisión humana recomendada")
