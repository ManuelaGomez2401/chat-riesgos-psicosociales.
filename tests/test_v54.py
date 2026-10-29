from src.messages import ACOMPANAMIENTO_RELACIONES,ACOMPANAMIENTO_GENERAL,SIN_INDICADORES

def test_relaciones_tiene_rutas():
    assert 'Recursos Humanos' in ACOMPANAMIENTO_RELACIONES
    assert 'Comité de Convivencia Laboral' in ACOMPANAMIENTO_RELACIONES
    assert 'no puede confirmar' in ACOMPANAMIENTO_RELACIONES

def test_relaciones_considera_supervisor():
    assert 'supervisor' in ACOMPANAMIENTO_RELACIONES
    assert 'otro canal' in ACOMPANAMIENTO_RELACIONES

def test_general_tiene_guia():
    assert 'Seguridad y Salud en el Trabajo' in ACOMPANAMIENTO_GENERAL

def test_sin_indicadores_no_da_garantia():
    assert 'no garantiza' in SIN_INDICADORES
