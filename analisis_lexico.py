
import re


TOKEN_REGEX = [
    ("COMENTARIO_MULTILINEA", r"/\*.*?\*/", re.DOTALL),
    ("COMENTARIO_SIMPLE", r"//.*"),

    ("OPERADOR_ARIT", r"\+\+|--|\+|-|\*|/|%|\^"),
    ("OPERADOR_REL", r"<=|>=|==|!=|<|>"),
    ("OPERADOR_LOG", r"\&\&|\&|\|\||\|"),
    ("ASIGNACION", r"="),
    ("SIMBOLO", r"[(){}.,;]"),
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

        # Manejo especial para ++
        if text[pos] == '+':
            next_pos = pos + 1
            while next_pos < len(text) and text[next_pos] in [' ', '\t', '\n']:
                if text[next_pos] == ';':
                    break
                next_pos += 1
            if next_pos < len(text) and text[next_pos] == '+':
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_ARIT", "++", linea, columna))
                pos = next_pos + 1
                continue

        # Manejo especial para --
        if text[pos] == '-':
            next_pos = pos + 1
            while next_pos < len(text) and text[next_pos] in [' ', '\t', '\n']:
                if text[next_pos] == ';':
                    break
                next_pos += 1
            if next_pos < len(text) and text[next_pos] == '-':
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_ARIT", "--", linea, columna))
                pos = next_pos + 1
                continue

        # && y &
        if text[pos] == '&':
            next_pos = pos + 1
            while next_pos < len(text) and text[next_pos] in [' ', '\t', '\n']:
                next_pos += 1
            if next_pos < len(text) and text[next_pos] == '&':
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_LOG", "&&", linea, columna))
                pos = next_pos + 1
                continue
            else:
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_LOG", "&", linea, columna))
                pos += 1
                continue

        # || y |
        if text[pos] == '|':
            next_pos = pos + 1
            while next_pos < len(text) and text[next_pos] in [' ', '\t', '\n']:
                next_pos += 1
            if next_pos < len(text) and text[next_pos] == '|':
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_LOG", "||", linea, columna))
                pos = next_pos + 1
                continue
            else:
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_LOG", "|", linea, columna))
                pos += 1
                continue

        # == y =
        if text[pos] == '=':
            next_pos = pos + 1
            while next_pos < len(text) and text[next_pos] in [' ', '\t', '\n']:
                next_pos += 1
            if next_pos < len(text) and text[next_pos] == '=':
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("OPERADOR_REL", "==", linea, columna))
                pos = next_pos + 1
                continue
            else:
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append(("ASIGNACION", "=", linea, columna))
                pos += 1
                continue

        for token in TOKEN_REGEX:
            token_type = token[0]
            regex = token[1]
            flag = token[2] if len(token) > 2 else 0

            pattern = re.compile(regex, flag)
            match = pattern.match(text, pos)

            if match:
                lexeme = match.group(0)

                # Verificación para enteros mal seguidos por punto o letra (ej. 12.a)
                if token_type == "NUMERO_ENTERO":
                    fin = pos + len(lexeme)
                    if fin < len(text) and text[fin] == '.':
                        # Si después del punto hay letra o no hay dígito, es error
                        if fin + 1 >= len(text) or not text[fin + 1].isdigit():
                            linea, columna = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea}, Columna {columna}: número mal formado después del punto")
                            pos = fin + 1
                            break


                # Verificación para dobles puntos en números reales (ej. 12.34.56)
               # Validación para NUMERO_REAL más estricta
                if token_type == "NUMERO_REAL":
                    fin = pos + len(lexeme)
                    if fin < len(text):
                        siguiente = text[fin]
                        if siguiente.isalpha() or siguiente == '.':
                            linea, columna = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea}, Columna {columna}: después de un número real no se esperaba '{siguiente}'")
                            pos = fin + 1
                            break


                if token_type in ["COMENTARIO_SIMPLE", "COMENTARIO_MULTILINEA"]:
                    pos = match.end()
                    break

                if token_type == "ESPACIO":
                    pos = match.end()
                    break

                if token_type == "DESCONOCIDO":
                    linea, columna = calcular_linea_columna(text, pos)
                    errors.append(f"Línea {linea}, Columna {columna}: carácter inválido '{lexeme}'")
                    pos = match.end()
                    break

                linea, columna = calcular_linea_columna(text, pos)
                tokens.append((token_type, lexeme, linea, columna))
                pos = match.end()
                break

        if not match:
            linea, columna = calcular_linea_columna(text, pos)
            errors.append(f"Línea {linea}, Columna {columna}: carácter no reconocido.")
            pos += 1

    return tokens, errors