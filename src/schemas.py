from typing import Literal
from pydantic import BaseModel, Field

Dimension = Literal["carga laboral","jornada y desconexión","relaciones y liderazgo","apoyo social y liderazgo","reconocimiento laboral","claridad del rol","autonomía y control","seguridad laboral","relaciones laborales"]

class DimensionIA(BaseModel):
    nombre: Dimension
    confianza: float = Field(ge=0, le=1)
    evidencia: str = Field(max_length=180)

class InterpretacionIA(BaseModel):
    relacion_laboral: Literal["clara","posible","no_clara"]
    dimensiones: list[DimensionIA] = []
    frecuencia: Literal["Una vez","Ocasionalmente","Varias veces por semana","Casi todos los días"] | None = None
    duracion: Literal["Pocos días","Varias semanas","Algunos meses","Más de seis meses"] | None = None
    impactos: list[Literal["Descanso","Concentración","Motivación","Relaciones","Vida personal","Tareas"]] = []
    pregunta_siguiente: str = Field(max_length=300)
    resumen_neutral: str = Field(max_length=600)
    expresion_nueva: str | None = Field(default=None,max_length=160)
