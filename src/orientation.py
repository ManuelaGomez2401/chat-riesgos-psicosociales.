def calcular(f,d,impactos,hay_condicion_desfavorable=True,):
 if not hay_condicion_desfavorable and not impactos:
  return {
   "tipo": "bienestar_positivo",
   "puntaje": 0,
   "version": "ORIENTACION_ACADEMICA_V2",
  }
 F={'Una vez':0,'Ocasionalmente':1,'Varias veces por semana':2,'Casi todos los días':3};D={'Pocos días':0,'Varias semanas':1,'Algunos meses':2,'Más de seis meses':3};p=F.get(f,0)+D.get(d,0)+min(len(impactos),2)
 if not impactos and p<=1:tipo='sin_indicadores'
 elif p<=1:tipo='puntual'
 elif p<=4:tipo='seguimiento'
 else:tipo='acompanamiento'
 return {'tipo':tipo,'puntaje':p,'version':'ORIENTACION_ACADEMICA_V1'}
