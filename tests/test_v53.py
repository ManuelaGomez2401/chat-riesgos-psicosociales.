import pandas as pd
from src.local import detectar
from src.ai_budget import MAX_CALLS_PER_SESSION

df=pd.DataFrame([{'expresion':'no doy abasto','variantes':'no alcanzo','dimension':'carga laboral','pregunta':'x'}])

def test_conducta_persecucion():
    dims=[x['dimension'] for x in detectar('me persigue cuando voy al baño',df)]
    assert 'relaciones y liderazgo' in dims

def test_comentario_no_deseado():
    dims=[x['dimension'] for x in detectar('me dice que soy muy linda y que quiere algo conmigo',df)]
    assert 'relaciones y liderazgo' in dims

def test_limite_sesion():assert MAX_CALLS_PER_SESSION==3
