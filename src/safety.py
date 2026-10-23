import re,unicodedata
P=["me quiero matar","quiero matarme","voy a matarme","me voy a matar","quiero morir","no quiero vivir","me quiero suicidar","acabar con mi vida","quitarme la vida","hacerme daño","seria mejor no despertar","no vale la pena seguir","quiero desaparecer para siempre","acabar con todo","ya tengo preparado como hacerlo"]
N=["no me quiero matar","no quiero matarme","no quiero morir","no pienso suicidarme","no voy a hacerme daño"]
def norm(x):
 x=unicodedata.normalize('NFD',str(x).lower());x=''.join(c for c in x if unicodedata.category(c)!='Mn');return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ\s]',' ',x)).strip()
def detectar_prioridad(x):
 t=norm(x)
 if any(norm(n) in t for n in N):return False
 return any(norm(p) in t for p in P)
PRIORIDAD="""**Siento mucho que estés pasando por esto. Gracias por decirlo. 💚**

Lo que compartiste requiere apoyo inmediato y está fuera del alcance de esta herramienta. Por favor, no enfrentes este momento a solas.

**Si existe un peligro inmediato o ya has hecho algo para lastimarte, llama al 123 o dirígete al servicio de urgencias más cercano.**

En Colombia puedes marcar la **Línea 106**, gratuita y disponible las 24 horas.

¿Estás en peligro inmediato en este momento? Responde **sí** o **no**."""
PELIGRO="""**Busca ayuda inmediata ahora.** Llama al **123**, pide a una persona cercana que permanezca contigo o dirígete a urgencias. También puedes marcar la **Línea 106**. Esta herramienta no sustituye atención de emergencia."""
NO_PELIGRO="""Gracias por responder. Aunque no haya un peligro inmediato, lo que compartiste merece apoyo humano hoy. Llama a la **Línea 106** o comunícate con una persona de confianza. Si te sientes en condiciones de continuar, cuéntame qué situación está influyendo en cómo te sientes."""
