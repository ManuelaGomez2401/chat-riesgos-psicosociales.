from src.safety import detectar_prioridad
def test_directo():assert detectar_prioridad('Me siento muy mal, me quiero matar')
def test_indirecto():assert detectar_prioridad('Sería mejor no despertar')
def test_plan():assert detectar_prioridad('Ya tengo preparado cómo hacerlo')
def test_negacion():assert not detectar_prioridad('No me quiero matar')
