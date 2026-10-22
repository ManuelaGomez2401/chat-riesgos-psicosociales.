import pandas as pd
from src.core import *
df=pd.read_csv('data/diccionario.csv')
def test_horario():assert'jornada y desconexión'in detectar('mis horarios son largos',df)
def test_trato():assert'relaciones y liderazgo'in detectar('me tratan mal',df)
def test_personal():assert relacion('problemas familiares')=='personal'
