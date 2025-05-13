import re

TOKEN_REGEX = [
    ("COMENTARIO_MULTILINEA", r"/\*.*?\*/", re.DOTALL),
    ("COMENTARIO_SIMPLE", r"//.*"),
    ("RESERVADA", r"\b(if|else|end|do|while|switch|case|int|float|main|cin|cout|then)\b"),
    ("OPERADOR_ARIT", r"\+\+|--|[+\-*/%^]"),
    ("OPERADOR_REL", r"<=|>=|==|!=|<|>"),
    ("OPERADOR_LOG", r"&&|\|\||!|&"),
    ("ASIGNACION", r"=(?!=)"),
    ("SIMBOLO", r"[(){}.,;]"),
    ("NUMERO_REAL", r"\b[+-]?\d+\.\d+\b"),
    ("NUMERO_ENTERO", r"\b[+-]?\d+\b"),
    ("IDENTIFICADOR", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("ESPACIO", r"\s+"),
    ("DESCONOCIDO", r"."),  # Último catch-all
]

def calcular_linea_columna(texto, index):
    linea = texto.count('\n', 0, index) + 1
    ultima_nueva_linea = texto.rfind('\n', 0, index)
    columna = index + 1 if ultima_nueva_linea == -1 else index - ultima_nueva_linea
    return linea, columna

def tokenize(text):
    tokens = []
    errors = []
    pos = 0
    length = len(text)

    while pos < length:
        # Detectar ++ y -- con saltos de línea ignorados
        if text[pos] in ['+', '-']:
            symbol = text[pos]
            next_pos = pos + 1
            while next_pos < length and text[next_pos] in [' ', '\t', '\n']:
                next_pos += 1
            if next_pos < length and text[next_pos] == symbol:
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_ARIT", symbol * 2, linea, columna))
                pos = next_pos + 1
                continue

        match = None
        for token_type, regex, *flags in TOKEN_REGEX:
            flag = flags[0] if flags else 0
            pattern = re.compile(regex, flag)
            match = pattern.match(text, pos)

            if match:
                lexeme = match.group(0)

                # NUMERO_ENTERO seguido de '.' no válido
                if token_type == "NUMERO_ENTERO":
                    fin = pos + len(lexeme)
                    if fin < length and text[fin] == '.':
                        if fin + 1 >= length or not text[fin + 1].isdigit():
                            linea, columna = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea}, Columna {columna+1}: error en '{text[fin]}', se esperaba un dígito después del punto")
                            pos = fin + 1
                            break

                # NUMERO_REAL seguido de letra o punto incorrecto
                if token_type == "NUMERO_REAL":
                    fin = pos + len(lexeme)
                    if fin < length:
                        siguiente = text[fin]
                        if siguiente.isalpha():
                            linea, columna = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea}, Columna {columna+1}: error en '{siguiente}', después de un número real no se esperaba '{siguiente}'")
                            pos = fin + 1
                            break
                        elif siguiente == '.':
                            # Se registra el número real correctamente
                            linea, columna = calcular_linea_columna(text, pos)
                            tokens.append((token_type, lexeme, linea, columna))
                            
                            # Y luego se reporta el error del punto adicional
                            linea_punto, columna_punto = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea_punto}, Columna {columna_punto+1}: carácter inválido '.' después de número real")
                            pos = fin + 1
                            break

                # Ignorar espacios y comentarios
                if token_type in ["ESPACIO", "COMENTARIO_SIMPLE", "COMENTARIO_MULTILINEA"]:
                    pos = match.end()
                    break

                if token_type == "DESCONOCIDO":
                    linea, columna = calcular_linea_columna(text, pos)
                    errors.append(f"Línea {linea}, Columna {columna}: carácter inválido '{lexeme}'")
                    pos = match.end()
                    break

                # Token válido
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append((token_type, lexeme, linea, columna))
                pos = match.end()
                break

        if not match:
            linea, columna = calcular_linea_columna(text, pos)
            errors.append(f"Línea {linea}, Columna {columna}: carácter no reconocido.")
            pos += 1

    return tokens, errors