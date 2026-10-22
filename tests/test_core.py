import pandas as pd
from src.core import detectar, relacion, frecuencia, duracion, impactos
df=pd.read_csv("data/diccionario.csv")
def dims(texto): return {x["dimension"] for x in detectar(texto,df)}
def test_horarios(): assert "jornada y desconexión" in dims("Mis horarios son muy largos")
def test_trato(): assert "relaciones y liderazgo" in dims("Me tratan mal")
def test_dos_dimensiones():
    d=dims("Mis horarios son largos y me tratan mal")
    assert "jornada y desconexión" in d and "relaciones y liderazgo" in d
def test_fuzzy(): assert "carga laboral" in dims("no doi abasto")
def test_relacion_personal(): assert relacion("es algo personal") == "personal"
def test_frecuencia(): assert frecuencia("3 veces por semana") == "Sucede varias veces por semana"
def test_duracion(): assert duracion("hace 3 meses") == "Algunos meses"
def test_impacto(): assert "Descanso" in impactos("no puedo dormir")
