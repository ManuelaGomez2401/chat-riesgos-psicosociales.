import pandas as pd
from src.core import *
df=pd.read_csv('data/diccionario.csv')
def test_horarios():assert'jornada y desconexión'in detectar('mis horarios son muy largos',df)
def test_trato():assert'relaciones y liderazgo'in detectar('me tratan mal',df)
def test_ambos():
 d=detectar('trabajo muchas horas y me gritan',df);assert'jornada y desconexión'in d and'relaciones y liderazgo'in d
def test_personal():assert relacion('es por problemas familiares')=='personal'
def test_frec():assert frecuencia('3 veces por semana')=='Varias veces por semana'
def test_dur():assert duracion('hace 3 meses')=='Algunos meses'
def test_imp():assert'Descanso'in impactos('no puedo dormir')
