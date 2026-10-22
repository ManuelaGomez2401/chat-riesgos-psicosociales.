import re, unicodedata
import pandas as pd
from rapidfuzz.fuzz import partial_ratio

def norm(x):
    x=unicodedata.normalize('NFD',str(x).lower().strip())
    x=''.join(c for c in x if unicodedata.category(c)!='Mn')
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ\s]',' ',x)).strip()

def detectar(texto,df):
    t=norm(texto); out=[]
    for _,r in df.iterrows():
        vals=[r.expresion]+([] if pd.isna(r.variantes) else str(r.variantes).split('|'))
        score=max(100 if norm(v) in t else partial_ratio(norm(v),t) for v in vals)
        if score>=78:
            out.append({'dimension':r.dimension_probable,'pregunta':r.pregunta_aclaratoria,'score':score})
    seen=set(); ans=[]
    for x in sorted(out,key=lambda z:z['score'],reverse=True):
        if x['dimension'] not in seen: ans.append(x); seen.add(x['dimension'])
    return ans[:3]

def relacion(t):
    t=norm(t)
    if any(x in t for x in ['ambas','las dos','trabajo y personal']): return 'ambas'
    if any(x in t for x in ['personal','familia','pareja','fuera del trabajo']): return 'personal'
    if any(x in t for x in ['no se','no estoy seguro','no estoy segura','tal vez']): return 'incierta'
    if any(x in t for x in ['trabajo','laboral','jefe','empresa','tareas','turno']): return 'trabajo'

def frecuencia(t):
    t=norm(t)
    m=re.search(r'(\d+)\s*veces?',t)
    if m:
        n=int(m.group(1)); return 'Ocurrió una vez' if n==1 else ('Sucede casi todos los días' if n>=4 else 'Sucede varias veces por semana')
    for cat,vals in {'Ocurrió una vez':['una vez','solo paso una vez'],'Sucede ocasionalmente':['a veces','de vez en cuando','ocasionalmente'],'Sucede varias veces por semana':['varias veces por semana','cada semana','muy seguido'],'Sucede casi todos los días':['todos los dias','cada dia','diariamente','siempre']}.items():
        if any(v in t for v in vals): return cat

def duracion(t):
    t=norm(t); m=re.search(r'(\d+)\s*mes',t)
    if m:
        n=int(m.group(1)); return 'Más de seis meses' if n>=6 else ('Algunos meses' if n>=2 else 'Varias semanas')
    for cat,vals in {'Pocos días':['ayer','pocos dias','esta semana'],'Varias semanas':['semanas','un mes'],'Algunos meses':['meses'],'Más de seis meses':['medio año','un año','años','año pasado']}.items():
        if any(v in t for v in vals): return cat

def impactos(t):
    t=norm(t)
    if any(x in t for x in ['no me afecta','ninguno','no ha afectado']): return ['Ninguno']
    mapa={'Descanso':['dormir','sueño','descanso','insomnio'],'Concentración':['concentracion','concentrarme','distraido','no me concentro'],'Motivación':['motivacion','sin ganas','desmotivado'],'Relaciones':['compañeros','equipo','conflictos'],'Vida personal':['familia','pareja','casa','vida personal'],'Tareas':['tareas','entregas','errores','rendimiento']}
    return [k for k,v in mapa.items() if any(x in t for x in v)]

def nivel(f,d,imps):
    fs={'Ocurrió una vez':0,'Sucede ocasionalmente':1,'Sucede varias veces por semana':2,'Sucede casi todos los días':3}
    ds={'Pocos días':0,'Varias semanas':1,'Algunos meses':2,'Más de seis meses':3}
    p=fs.get(f,0)+ds.get(d,0)+min(len([x for x in imps if x!='Ninguno']),2)
    return 'Situación laboral puntual' if p<=1 else ('Posible factor psicosocial recurrente' if p<=4 else 'Revisión humana recomendada')
