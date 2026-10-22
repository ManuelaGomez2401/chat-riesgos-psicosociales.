from src.orientacion import calcular_orientacion

def test_general():
    assert calcular_orientacion("Ocurrió una vez","Desde hace pocos días",["Ninguno de los anteriores"])[0] == "Orientación general"

def test_contacto():
    assert calcular_orientacion("Sucede casi todos los días","Desde hace algunos meses",["Descanso","Vida personal"])[0] == "Contacto humano recomendado"
