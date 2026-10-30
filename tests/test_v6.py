from src.emotional_support import detectar_conceptos, ayudas_para

def test_ansiedad_local():
    assert 'ANSIEDAD' in detectar_conceptos('estoy muy ansioso y preocupado')

def test_panico_local():
    c=detectar_conceptos('me falta el aire y se me acelera el corazón')
    assert 'PANICO' in c or 'SINTOMAS_FISICOS' in c

def test_ayuda_ansiedad():
    ayudas=ayudas_para(['ANSIEDAD'])
    assert ayudas and ayudas[0]['codigo']=='ANSIEDAD'
