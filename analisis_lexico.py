import re  # Se importa el módulo 're' para trabajar con expresiones regulares

# Lista de tuplas que define los tipos de tokens junto con su expresión regular
TOKEN_REGEX = [
    ("COMENTARIO_MULTILINEA", r"/\*.*?\*/", re.DOTALL),  # Comentarios tipo /* ... */
    ("COMENTARIO_SIMPLE", r"//.*"),                     # Comentarios tipo //
    ("RESERVADA", r"\b(if|else|end|do|while|switch|case|int|float|main|cin|cout|then|repeat|read|write|until|true|false)\b"),
    ("OPERADOR_ARIT", r"\+\+|--|[+\-*/%^]"),             # Operadores aritméticos
    ("OPERADOR_REL", r"<<|>>|<=|>=|==|!=|<|>"),          # << y >> primero
    ("OPERADOR_LOG", r"&&|\|\||!|&"),                    # Operadores lógicos
    ("ASIGNACION", r"=(?!=)"),                           # Operador de asignación
    ("SIMBOLO", r"[](){}.,;:;[]"),                       # Símbolos comunes
    ("NUMERO_REAL", r"\b[+-]?\d+\.\d+\b"),               # Números con punto decimal
    ("NUMERO_ENTERO", r"\b[+-]?\d+\b"),                  # Números enteros
    ("IDENTIFICADOR", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),    # Nombres de variables o funciones
    ("ESPACIO", r"\s+"),                                 # Espacios en blanco
    ("DESCONOCIDO", r"."),                               # Cualquier otro carácter
]

# Función para calcular la línea y columna de un carácter en un texto dado su índice
def calcular_linea_columna(texto, index):
    linea = texto.count('\n', 0, index) + 1
    ultima_nueva_linea = texto.rfind('\n', 0, index)
    columna = index + 1 if ultima_nueva_linea == -1 else index - ultima_nueva_linea
    return linea, columna

# Función principal que recibe un texto y devuelve los tokens reconocidos y los errores encontrados
def tokenize(text):
    tokens = []  # Lista de tokens válidos
    errors = []  # Lista de errores
    pos = 0
    length = len(text)

    while pos < length:
        # Caso especial para detectar operadores ++ y -- incluso si hay espacios o saltos de línea entre ellos
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
        # Intentamos hacer match con cada una de las expresiones regulares
        for token_type, regex, *flags in TOKEN_REGEX:
            flag = flags[0] if flags else 0
            pattern = re.compile(regex, flag)
            match = pattern.match(text, pos)

            if match:
                lexeme = match.group(0)

                # Validación: número entero seguido de un punto mal formado 
                if token_type == "NUMERO_ENTERO":
                    fin = pos + len(lexeme)
                    if fin < length and text[fin] == '.':
                        if fin + 1 >= length or not text[fin + 1].isdigit():
                            linea, columna = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea}, Columna {columna+1}: error en '{text[fin]}', se esperaba un dígito después del punto")
                            pos = fin + 1
                            break

                # Validación: número real mal seguido de letra o punto extra
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
                            # Agregar el token como válido
                            linea, columna = calcular_linea_columna(text, pos)
                            tokens.append((token_type, lexeme, linea, columna))
                            # Y registrar el error por el punto adicional
                            linea_punto, columna_punto = calcular_linea_columna(text, fin)
                            errors.append(f"Línea {linea_punto}, Columna {columna_punto+1}: carácter inválido '.' después de número real")
                            pos = fin + 1
                            break

                # Ignorar espacios y comentarios (no se agregan a tokens)
                if token_type in ["ESPACIO", "COMENTARIO_SIMPLE", "COMENTARIO_MULTILINEA"]:
                    pos = match.end()
                    break

                # Caracter inválido
                if token_type == "DESCONOCIDO":
                    linea, columna = calcular_linea_columna(text, pos)
                    errors.append(f"Línea {linea}, Columna {columna}: carácter inválido '{lexeme}'")
                    pos = match.end()
                    break

                # Token válido, se agrega a la lista
                linea, columna = calcular_linea_columna(text, pos)
                tokens.append((token_type, lexeme, linea, columna))
                pos = match.end()
                break

        # Si no se hizo match con ninguna expresión regular
        if not match:
            linea, columna = calcular_linea_columna(text, pos)
            errors.append(f"Línea {linea}, Columna {columna}: carácter no reconocido.")
            pos += 1

    return tokens, errors
