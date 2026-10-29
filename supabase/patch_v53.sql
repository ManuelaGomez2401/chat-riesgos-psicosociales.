-- Expresiones de exploración. No confirman acoso; solo activan preguntas de hechos concretos.
insert into public.dictionary_entries(expression,variants,dimension,question,status,source)
values
('me persigue','no me deja tranquila|no me deja tranquilo|me sigue cuando voy al baño','relaciones y liderazgo','¿Qué comportamientos concretos han ocurrido y con qué frecuencia?','active','manual_academic'),
('me hace comentarios personales no deseados','comenta sobre mi cuerpo|me dice que soy muy linda|me dice que soy muy lindo|quiere algo conmigo|hace insinuaciones','relaciones y liderazgo','¿Qué comentarios o conductas han ocurrido y cómo has respondido?','active','manual_academic')
on conflict(expression) do update set
 variants=excluded.variants,
 dimension=excluded.dimension,
 question=excluded.question,
 status='active';
