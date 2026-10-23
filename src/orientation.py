def calcular(frecuencia,duracion,impactos):
    f={"Una vez":0,"Ocasionalmente":1,"Varias veces por semana":2,"Casi todos los días":3};d={"Pocos días":0,"Varias semanas":1,"Algunos meses":2,"Más de seis meses":3}
    p=f.get(frecuencia,0)+d.get(duracion,0)+min(len(impactos),2)
    nivel="Situación laboral puntual" if p<=1 else ("Posible factor psicosocial recurrente" if p<=4 else "Revisión humana recomendada")
    return {"orientacion":nivel,"puntaje":p,"version":"ORIENTACION_V2"}
