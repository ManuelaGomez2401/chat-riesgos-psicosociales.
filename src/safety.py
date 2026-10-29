import re, unicodedata
PRIORITARIAS=["me quiero matar","quiero matarme","voy a matarme","quiero morir","no quiero vivir","me quiero suicidar","acabar con mi vida","quitarme la vida","hacerme daño","seria mejor no despertar","no vale la pena seguir","acabar con todo"]
NEGADAS=["no me quiero matar","no quiero matarme","no quiero morir","no voy a hacerme daño"]
def norm(x):
 x=unicodedata.normalize('NFD',str(x).lower());x=''.join(c for c in x if unicodedata.category(c)!='Mn');return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ\s]',' ',x)).strip()
def detectar_prioridad(x):
 t=norm(x)
 if any(norm(n) in t for n in NEGADAS):return False
 return any(norm(p) in t for p in PRIORITARIAS)
PRIORIDAD="""**Siento mucho que estés pasando por esto. Gracias por decirlo. 💚**

Lo que compartiste requiere apoyo inmediato y está fuera del alcance de esta herramienta. Si existe peligro inmediato, llama al **123** o dirígete a urgencias. En Colombia puedes marcar la **Línea 106**.

¿Estás en peligro inmediato en este momento? Responde **sí** o **no**."""
