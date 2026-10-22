import unicodedata
import pandas as pd


def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower().strip())
    return "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )


def encontrar_coincidencia(mensaje, df):
    mensaje_normalizado = normalizar(mensaje)

    for _, fila in df.iterrows():
        expresiones = [str(fila["expresion"])]

        if pd.notna(fila.get("variantes")):
            expresiones.extend(str(fila["variantes"]).split("|"))

        if any(
            normalizar(expresion) in mensaje_normalizado
            for expresion in expresiones
            if str(expresion).strip()
        ):
            return fila

    return None
