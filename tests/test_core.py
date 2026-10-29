from src.anonymizer import anonimizar
from src.orientation import calcular
from src.safety import detectar_prioridad
def test_anon():assert '[CORREO]' in anonimizar('a@b.com')
def test_prioridad():assert detectar_prioridad('me quiero matar')
def test_resultado():assert calcular('Casi todos los días','Algunos meses',['Descanso'])['tipo']=='acompanamiento'
