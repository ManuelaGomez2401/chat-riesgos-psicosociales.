import re, unicodedata, pandas as pd
from rapidfuzz.fuzz import partial_ratio
CATS={'carga laboral':['carga','sobrecarga','mucho trabajo','muchas tareas','plazo','urgente','para ayer'],'jornada y desconexión':['horario','jornada','turno','horas extra','salgo tarde','muchas horas','sin descanso','sin pausas','desconectarme'],'relaciones y liderazgo':['trato','tratan mal','maltrato','gritan','humillan','insultan','irrespeto','burlan','jefe','jefa'],'apoyo social y liderazgo':['no me escuchan','no me apoyan','ignoran','no me ayudan'],'reconocimiento laboral':['no reconocen','no valoran','solo ven mis errores'],'claridad del rol':['funciones','no se que hacer','cambian mis tareas'],'autonomía y control':['no puedo decidir','sin autonomia','todo lo deciden'],'seguridad laboral':['me van a echar','no me renuevan','perder el trabajo'],'relaciones laborales':['mal ambiente','conflicto','peleas','equipo dividido']}
def norm(x):
 x=unicodedata.normalize('NFD',str(x).lower().strip());x=''.join(c for c in x if unicodedata.category(c)!='Mn');return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ\s]',' ',x)).strip()
def detectar(t,df):
 n=norm(t);out=[]
 for _,r in df.iterrows():
  vals=[r.expresion]+str(r.variantes).split('|');score=max(100 if norm(v) in n else partial_ratio(norm(v),n) for v in vals)
  if score>=78:out.append((r.dimension,score))
 for d,ks in CATS.items():
  if any(norm(k) in n for k in ks):out.append((d,90))
 seen=set();ans=[]
 for d,s in sorted(out,key=lambda z:z[1],reverse=True):
  if d not in seen:ans.append(d);seen.add(d)
 return ans[:3]
def relacion(t):
 t=norm(t)
 if any(x in t for x in ['ambas','las dos','trabajo y personal']):return'ambas'
 if any(x in t for x in ['personal','familia','pareja','fuera del trabajo']):return'personal'
 if any(x in t for x in ['no se','no estoy seguro','no estoy segura','tal vez']):return'incierta'
 if any(x in t for x in ['trabajo','laboral','jefe','empresa','tareas','turno']):return'trabajo'
def frecuencia(t):
 t=norm(t);m=re.search(r'(\d+)\s*veces?',t)
 if m:
  n=int(m.group(1));return'Una vez' if n==1 else('Casi todos los días' if n>=4 else'Varias veces por semana')
 for k,v in {'Una vez':['una vez'],'Ocasionalmente':['a veces','de vez en cuando'],'Varias veces por semana':['varias veces','cada semana','muy seguido'],'Casi todos los días':['todos los dias','cada dia','diariamente','siempre']}.items():
  if any(x in t for x in v):return k
def duracion(t):
 t=norm(t);m=re.search(r'(\d+)\s*mes',t)
 if m:
  n=int(m.group(1));return'Más de seis meses' if n>=6 else('Algunos meses' if n>=2 else'Varias semanas')
 for k,v in {'Pocos días':['ayer','pocos dias','esta semana'],'Varias semanas':['semanas','un mes'],'Algunos meses':['meses'],'Más de seis meses':['medio año','un año','años','año pasado']}.items():
  if any(x in t for x in v):return k
def impactos(t):
 t=norm(t)
 if any(x in t for x in ['no me afecta','ninguno','no ha afectado']):return['Ninguno']
 mp={'Descanso':['dormir','sueño','descanso','insomnio'],'Concentración':['concentracion','concentrarme','distraido'],'Motivación':['motivacion','sin ganas','desmotivado'],'Relaciones':['compañeros','equipo','conflictos'],'Vida personal':['familia','pareja','casa','vida personal'],'Tareas':['tareas','entregas','errores','rendimiento']}
 return[k for k,v in mp.items() if any(x in t for x in v)]
def nivel(f,d,i):
 fs={'Una vez':0,'Ocasionalmente':1,'Varias veces por semana':2,'Casi todos los días':3};ds={'Pocos días':0,'Varias semanas':1,'Algunos meses':2,'Más de seis meses':3};p=fs.get(f,0)+ds.get(d,0)+min(len([x for x in i if x!='Ninguno']),2);return'Situación laboral puntual' if p<=1 else('Posible factor psicosocial recurrente' if p<=4 else'Revisión humana recomendada')
