from src.core import relacion

def test_aun_no_lo_tengo_claro(): assert relacion('aún no lo tengo claro') == 'incierta'
def test_aun_no_lo_se(): assert relacion('Aun no lo se') == 'incierta'
def test_todavia_no_se(): assert relacion('todavía no sé') == 'incierta'
def test_personal(): assert relacion('es por problemas familiares') == 'personal'
def test_trabajo(): assert relacion('creo que es por el trabajo') == 'trabajo'
