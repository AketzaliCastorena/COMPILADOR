
import re

TOKEN_REGEX = [
    ("COMENTARIO_MULTILINEA", r"/\*.*?\*/", re.DOTALL),
    ("COMENTARIO_SIMPLE", r"//.*"),
    ("NUMERO_REAL", r"[+-]?\d+\.\d+"),  # Primero los reales correctos
    ("NUMERO_ENTERO", r"[+-]?\d+"),       # Luego enteros
    ("OPERADOR_ARIT", r"\+\+|--|\+|-|\*|/|%|\^"),
    ("OPERADOR_REL", r"<=|>=|==|!=|<|>"),
    ("OPERADOR_LOG", r"\&\&|\|\||!"),
    ("ASIGNACION", r"="),
    ("SIMBOLO", r"[(){}.,;]"),
    ("RESERVADA", r"\b(if|else|end|do|while|switch|case|int|float|main|cin|cout)\b"),
    ("IDENTIFICADOR", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("ESPACIO", r"\s+"),
    ("DESCONOCIDO", r"."),  # Lo que no encaje en nada, va como error
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
        
        if pos+1 < len(text):
            # Verificar por operadores de 2 caracteres (++, --)
            if text[pos:pos+2] == "++":
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_ARIT", "++", linea, columna))
                pos += 2
                continue
            elif text[pos:pos+2] == "--":
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_ARIT", "--", linea, columna))
                pos += 2
                continue 
        
        for token in TOKEN_REGEX:
            token_type = token[0]
            regex = token[1]
            flag = token[2] if len(token) > 2 else 0

            pattern = re.compile(regex, flag)
            match = pattern.match(text, pos)

            if match:
                lexeme = match.group(0)

                if token_type == "NUMERO_ENTERO":
                    if pos + len(lexeme) < len(text) and text[pos + len(lexeme)] == ".":
                        sig = text[pos + len(lexeme):]
                        if re.match(r"\.[a-zA-Z_]", sig):
                            linea, columna = calcular_linea_columna(text, pos + len(lexeme))
                            errors.append(f"Línea {linea}, Columna {columna}: carácter inválido '.'")
                            pos += len(lexeme) + 1
                            break

                if token_type == "NUMERO_REAL":
                    fin = pos + len(lexeme)
                    if fin < len(text) and re.match(r"[a-zA-Z_]", text[fin]):
                        linea, columna = calcular_linea_columna(text, fin)
                        errors.append(f"Línea {linea}, Columna {columna}: carácter inválido '{text[fin]}'")
                        pos = fin + 1
                        break
                
                if token_type == "COMENTARIO_SIMPLE" or token_type == "COMENTARIO_MULTILINEA":
                    pos = match.end()
                    break
                
                if token_type == "ESPACIO":
                    pass
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
