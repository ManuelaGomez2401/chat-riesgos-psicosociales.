import inspect
from src import storage

def test_crear_sesion_usa_uuid_local():
    source = inspect.getsource(storage.crear_sesion)
    assert "uuid.uuid4" in source
    assert 'returning="minimal"' in source

def test_resultado_no_usa_upsert():
    source = inspect.getsource(storage.guardar_resultado)
    assert ".insert(" in source
    assert ".upsert(" not in source
