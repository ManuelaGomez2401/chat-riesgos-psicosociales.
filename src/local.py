import re,unicodedata,pandas as pd
from rapidfuzz.fuzz import partial_ratio

CATEGORIAS={
 "carga laboral":["carga","sobrecarga","mucho trabajo","muchas tareas","todo urgente","no doy abasto"],
 "jornada y desconexión":["horario","jornada","turno","horas extra","muchas horas","sin descanso"],
 "relaciones y liderazgo":["me persigue","no me deja tranquila","no me deja tranquilo","me hostiga","me intimida","me acosa","comentarios sobre mi cuerpo","me dice que soy linda","me dice que soy lindo","quiere algo conmigo","insinua cosas","me grita","me humilla","me trata mal"],
 "apoyo social y liderazgo":["no me escucha","no me apoya","me ignora"],
 "reconocimiento laboral":["no me valoran","no reconocen","solo ven mis errores"],
 "claridad del rol":["no se que esperan","funciones","me cambian las tareas"],
 "autonomía y control":["no puedo decidir","todo lo deciden"],
 "seguridad laboral":["me van a echar","no me renuevan","perder el trabajo"],
 "relaciones laborales":["mal ambiente","conflictos","peleas","me excluyen"],
}

def norm(x):
 x=unicodedata.normalize('NFD',str(x).lower());x=''.join(c for c in x if unicodedata.category(c)!='Mn');return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ\s]',' ',x)).strip()

def relacion(x):
 t=norm(x)
 if any(v in t for v in ['ambas','las dos','trabajo y personal']):return'ambas'
 if any(v in t for v in ['personal','familia','pareja','fuera del trabajo']):return'personal'
 if any(v in t for v in ['no se','aun no se','todavia no se','no lo tengo claro','no estoy seguro','tal vez']):return'incierta'
 if any(v in t for v in ['trabajo','laboral','jefe','jefa','empresa','tareas','turno']):return'trabajo'

def detectar(x,df):
 t=norm(x);out=[]
 for _,r in df.iterrows():
  vals=[str(r.expresion)]+str(r.variantes or '').split('|')
  score=max(100 if norm(v) in t else partial_ratio(norm(v),t) for v in vals if v)
  if score>=78:out.append({'dimension':str(r.dimension),'expresion':str(r.expresion),'confianza':round(score/100,2),'pregunta':str(r.pregunta)})
 for dimension,frases in CATEGORIAS.items():
  if any(norm(frase) in t for frase in frases):
   out.append({'dimension':dimension,'expresion':'categoría local','confianza':0.92,'pregunta':'¿Qué comportamientos concretos han ocurrido y con qué frecuencia?'})
 seen=set();ans=[]
 for i in sorted(out,key=lambda z:z['confianza'],reverse=True):
  if i['dimension'] not in seen:ans.append(i);seen.add(i['dimension'])
 return ans[:3]

def frecuencia(x):
 t=norm(x);m=re.search(r'(\d+)\s*veces?',t)
 if m:
  n=int(m.group(1));return'Una vez' if n==1 else('Casi todos los días' if n>=4 else'Varias veces por semana')
 for k,v in {'Una vez':['una vez'],'Ocasionalmente':['a veces','de vez en cuando'],'Varias veces por semana':['varias veces','cada semana'],'Casi todos los días':['todos los dias','cada dia','siempre']}.items():
  if any(z in t for z in v):return k

def duracion(x):
 t=norm(x);m=re.search(r'(\d+)\s*mes',t)
 if m:
  n=int(m.group(1));return'Más de seis meses' if n>=6 else('Algunos meses' if n>=2 else'Varias semanas')
 for k,v in {'Pocos días':['ayer','pocos dias','esta semana'],'Varias semanas':['semanas','un mes'],'Algunos meses':['meses'],'Más de seis meses':['medio año','un año','años']}.items():
  if any(z in t for z in v):return k

def impactos(x):
 t=norm(x)
 if any(z in t for z in ['no me afecta','ninguno','estoy bien','me siento bien']):return[]
 mp={'Descanso':['dormir','sueño','descanso','insomnio'],'Concentración':['concentracion','concentrarme'],'Motivación':['motivacion','sin ganas'],'Relaciones':['compañeros','equipo','conflictos'],'Vida personal':['familia','pareja','casa'],'Tareas':['tareas','entregas','errores','rendimiento']}
 return[k for k,v in mp.items() if any(z in t for z in v)]

EXPRESIONES_BIENESTAR = [
 "me siento bien",
 "estoy bien",
 "me siento tranquilo",
 "me siento tranquila",
 "estoy tranquilo",
 "estoy tranquila",
 "me siento feliz",
 "me siento contento",
 "me siento contenta",
 "me gusta mi trabajo",
 "todo esta bien",
 "las cosas van bien",
 "me siento apoyado",
 "me siento apoyada",
 "me siento valorado",
 "me siento valorada",
]

EXPRESIONES_DESFAVORABLES = [
 "pero",
 "aunque",
 "sin embargo",
 "me grita",
 "me humilla",
 "me persigue",
 "me hostiga",
 "me acosa",
 "me amenaza",
 "me sobre exige",
 "me sobreexige",
 "demasiado trabajo",
 "muchas tareas",
 "no doy abasto",
 "no me escuchan",
 "no me apoyan",
 "no me valoran",
 "horarios largos",
 "trabajo muchas horas",
 "no puedo desconectarme",
 "me van a echar",
 "mal ambiente",
]
print(
    "REGLAS_BIENESTAR_CARGADAS:",
    len(EXPRESIONES_BIENESTAR),
    len(EXPRESIONES_DESFAVORABLES),
    flush=True,
)


def detectar_bienestar_positivo(texto):
    texto_normalizado = norm(texto)

    return any(
        expresion in texto_normalizado
        for expresion in EXPRESIONES_BIENESTAR
    )


def detectar_condicion_desfavorable(texto):
    texto_normalizado = norm(texto)

    return any(
        expresion in texto_normalizado
        for expresion in EXPRESIONES_DESFAVORABLES
    )
