
import re

TOKEN_REGEX = [
    ("COMENTARIO_MULTILINEA", r"/\*.*?\*/", re.DOTALL),
    ("COMENTARIO_SIMPLE", r"//.*"),
    ("NUMERO_REAL", r"[+-]?\d+\.\d+"),
    ("NUMERO_ENTERO", r"[+-]?\d+"),
    ("OPERADOR_ARIT", r"\+\+|--|\+|-|\*|/|%|\^"),
    ("OPERADOR_REL", r"<=|>=|==|!=|<|>"),
    ("OPERADOR_LOG", r"\&\&|\|\||!"),
    ("ASIGNACION", r"="),
    ("SIMBOLO", r"[(){},;]"),
    ("RESERVADA", r"\b(if|else|end|do|while|switch|case|int|float|main|cin|cout)\b"),
    ("IDENTIFICADOR", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("ESPACIO", r"\s+"),
    ("DESCONOCIDO", r"."),
]

def calcular_linea_columna(texto, index):
    linea = texto.count('\n', 0, index) + 1
    ultima_nueva_linea = texto.rfind('\n', 0, index)
    if ultima_nueva_linea == -1:
        columna = index + 1
    else:
        columna = index - ultima_nueva_linea
    return linea, columna

def tokenize(text):
    tokens = []
    errors = []
    pos = 0
    while pos < len(text):
        match = None
        for token_type, regex, *flags in TOKEN_REGEX:
            flag = flags[0] if flags else 0
            pattern = re.compile(regex, flag)
            match = pattern.match(text, pos)
            if match:
                lexeme = match.group(0)
                if token_type == "ESPACIO":
                    pass  # Ignorar
                elif token_type == "DESCONOCIDO":
                    linea, columna = calcular_linea_columna(text, pos)
                    errors.append(f"Línea {linea}, Columna {columna}: carácter inválido '{lexeme}'")
                else:
                    linea, columna = calcular_linea_columna(text, pos)
                    tokens.append((token_type, lexeme, linea, columna))
                pos = match.end()
                break
        if not match:
            linea, columna = calcular_linea_columna(text, pos)
            errors.append(f"Línea {linea}, Columna {columna}: carácter no reconocido.")
            pos += 1
    return tokens, errors
