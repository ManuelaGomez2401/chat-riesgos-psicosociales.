"""Texto de instrucciones para que Gemini contribuya a la conversación, no solo clasifique."""
CONTEXT_OBJECTIVE = """
Analiza el relato laboral completo. Identifica hasta tres dimensiones permitidas sin diagnosticar ni confirmar acoso.
Redacta UNA sola pregunta de profundización que use detalles del mensaje y que solicite la información más útil que falte.
No preguntes '¿representa lo que quisiste expresar?'. No repitas una pregunta ya realizada.
Si la frase parece nueva o coloquial, devuelve en expresion_nueva una versión breve y reutilizable de esa expresión.
"""
