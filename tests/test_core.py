import pandas as pd
from src.core import *
df=pd.read_csv('data/diccionario.csv')
def test_fuzzy(): assert detectar('no doi abasto',df)[0]['dimension']=='carga laboral'
def test_relacion(): assert relacion('creo que es algo personal')=='personal'
def test_frecuencia(): assert frecuencia('me pasa 3 veces por semana')=='Sucede varias veces por semana'
def test_duracion(): assert duracion('desde hace 3 meses')=='Algunos meses'
def test_impacto(): assert 'Descanso' in impactos('no puedo dormir')
def test_sin_relacion(): assert nivel('Ocurrió una vez','Pocos días',['Ninguno'])=='Situación laboral puntual'
