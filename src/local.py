import re,unicodedata,pandas as pd
from rapidfuzz.fuzz import partial_ratio
CAT={"carga laboral":["carga","sobrecarga","mucho trabajo","muchas tareas","urgente"],"jornada y desconexión":["horario","jornada","turno","horas extra","muchas horas","sin descanso"],"relaciones y liderazgo":["trato","tratan mal","gritan","humillan","hostiga","intimida","jefe","jefa"],"apoyo social y liderazgo":["no me escuchan","no me apoyan","ignoran"],"reconocimiento laboral":["no reconocen","no valoran"],"claridad del rol":["funciones","no se que hacer"],"autonomía y control":["no puedo decidir","sin autonomia"],"seguridad laboral":["me van a echar","no me renuevan"],"relaciones laborales":["mal ambiente","conflicto","peleas"]}
def norm(x):
 x=unicodedata.normalize('NFD',str(x).lower());x=''.join(c for c in x if unicodedata.category(c)!='Mn');return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ\s]',' ',x)).strip()
def relacion(x):
 t=norm(x)
 if any(v in t for v in ['ambas','las dos','trabajo y personal']):return'ambas'
 if any(v in t for v in ['personal','familia','pareja','fuera del trabajo']):return'personal'
 if any(v in t for v in ['no se','aun no se','aun no lo se','todavia no se','no lo tengo claro','no estoy seguro','no estoy segura','quizas','tal vez']):return'incierta'
 if any(v in t for v in ['trabajo','laboral','jefe','empresa','tareas','turno']):return'trabajo'
def detectar(x,df):
 t=norm(x);out=[]
 for _,r in df.iterrows():
  vals=[r.expresion]+str(r.variantes).split('|');s=max(100 if norm(v) in t else partial_ratio(norm(v),t) for v in vals)
  if s>=78:out.append(r.dimension)
 for d,ks in CAT.items():
  if any(norm(k) in t for k in ks):out.append(d)
 return list(dict.fromkeys(out))[:3]
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
