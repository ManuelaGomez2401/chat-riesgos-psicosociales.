from src.anonymizer import anonimizar
from src.orientation import calcular
from src.fusion import fusionar

def test_anonimiza():assert '[CORREO]' in anonimizar('escribe a prueba@correo.com')
def test_orientacion_local():assert calcular('Casi todos los días','Algunos meses',['Descanso','Vida personal'])['orientacion']=='Revisión humana recomendada'
def test_fallback():assert fusionar([],None)['fuente']=='pregunta de respaldo'
