from src.orientation import calcular
from src.messages import BIENVENIDA,SIN_INDICADORES,ACOMPANAMIENTO
from src.local import relacion

def test_bienvenida_extensa():assert len(BIENVENIDA)>500
def test_cierre_positivo():assert 'volver a este espacio' in SIN_INDICADORES
def test_cierre_acompanamiento():assert 'persona capacitada' in ACOMPANAMIENTO
def test_sin_indicadores():assert calcular('Una vez','Pocos días',[])['tipo']=='sin_indicadores'
def test_incierta():assert relacion('aún no lo tengo claro')=='incierta'
