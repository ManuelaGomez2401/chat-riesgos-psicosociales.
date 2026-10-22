import pandas as pd
from src.detector import normalizar, encontrar_coincidencia
from src.orientacion import calcular_orientacion


def test_normalizar():
    assert normalizar("  PRESIÓN  ") == "presion"


def test_encontrar():
    df = pd.read_csv("data/diccionario.csv")
    fila = encontrar_coincidencia("No doy abasto", df)
    assert fila is not None
    assert fila["dimension_probable"] == "carga laboral"


def test_orientacion_general():
    nivel, _ = calcular_orientacion(
        "Ocurrió una vez",
        "Desde hace pocos días",
        ["Ninguno de los anteriores"],
    )
    assert nivel == "Orientación general"


def test_contacto_humano():
    nivel, _ = calcular_orientacion(
        "Sucede casi todos los días",
        "Desde hace algunos meses",
        ["Descanso", "Vida personal"],
    )
    assert nivel == "Contacto humano recomendado"
