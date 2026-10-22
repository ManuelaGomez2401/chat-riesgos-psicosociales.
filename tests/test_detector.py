import pandas as pd
from src.detector import normalizar, detectar_coincidencias

DF = pd.read_csv("data/diccionario.csv")

def test_normalizacion():
    assert normalizar("  PRESIÓN  ") == "presion"

def test_error_ortografico_simple():
    hallazgos = detectar_coincidencias("No doi abasto", DF)
    assert hallazgos and hallazgos[0]["dimension"] == "carga laboral"

def test_multiples_dimensiones():
    hallazgos = detectar_coincidencias("No doy abasto y mi jefe no me escucha", DF)
    dims = {h["dimension"] for h in hallazgos}
    assert "carga laboral" in dims
    assert "apoyo social y liderazgo" in dims

def test_negacion_basica():
    hallazgos = detectar_coincidencias("No estoy mamado", DF)
    assert not any(h["expresion"] == "estoy mamado" for h in hallazgos)
