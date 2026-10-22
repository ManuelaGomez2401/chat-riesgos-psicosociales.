import pandas as pd
from src.core import *
df=pd.read_csv('data/diccionario.csv')
def dd(x):return[h['dimension'] for h in detectar(x,df)]
def test_horarios():assert'jornada y desconexión'in dd('mis horarios son muy largos')
def test_trato():assert'relaciones y liderazgo'in dd('me tratan mal')
def test_dos():
 d=dd('trabajo muchas horas y me gritan');assert'jornada y desconexión'in d and'relaciones y liderazgo'in d
def test_personal():assert relacion('problemas familiares')=='personal'
def test_frec():assert frecuencia('3 veces por semana')=='Varias veces por semana'
def test_dur():assert duracion('3 meses')=='Algunos meses'
def test_imp():assert'Descanso'in impactos('no puedo dormir')
