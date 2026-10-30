from functools import lru_cache
from pathlib import Path
import pandas as pd
from src.local import norm

XLSX = Path(__file__).resolve().parents[1] / 'data' / 'diccionario_bienestar_psicologico_con_asistencia.xlsx'

@lru_cache(maxsize=1)
def cargar():
    expresiones = pd.read_excel(XLSX, sheet_name='diccionario', engine='openpyxl').fillna('')
    asistencia = pd.read_excel(XLSX, sheet_name='asistencia', engine='openpyxl').fillna('')
    return expresiones, asistencia

def detectar_conceptos(texto):
    expresiones,_ = cargar(); t=norm(texto); encontrados=[]
    # Priorizar expresiones largas para evitar que una palabra corta domine.
    for _,r in expresiones.assign(_len=expresiones['expresion_normalizada'].astype(str).str.len()).sort_values('_len',ascending=False).iterrows():
        e=norm(r.get('expresion_normalizada') or r.get('expresion'))
        if e and e in t:
            c=str(r.get('concepto','')).upper()
            if c and c!='REQUIERE_CONTEXTO' and c not in encontrados: encontrados.append(c)
    return encontrados[:4]

def ayudas_para(conceptos, maximo=2):
    _,asistencia=cargar(); resultados=[]
    for _,r in asistencia.iterrows():
        detonantes={x.strip().upper() for x in str(r['detonantes_conceptos']).split('|')}
        if any(c in detonantes for c in conceptos) and str(r.get('activo','SI')).upper()=='SI':
            resultados.append({k:str(r.get(k,'')) for k in asistencia.columns})
        if len(resultados)>=maximo: break
    return resultados

def formatear_ayuda(a):
    return f"""### Apoyo práctico: {a['nombre_visible']}

{a['mensaje_introduccion']}

{a['recomendaciones']}

**Cuándo buscar ayuda:** {a['nota_escalamiento']}

_Esta orientación es general, no diagnóstica y no reemplaza una valoración profesional._"""
