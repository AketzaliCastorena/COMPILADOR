class Token:
    def __init__(self, tipo, lexema, linea, columna):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna

    def __str__(self):
        return f"{self.tipo}('{self.lexema}') en L{self.linea} C{self.columna}"

class ASTNode:
    def __init__(self, tipo, valor=None, linea=None, columna=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.hijos = []

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)


class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.errores = []

    def obtener_token(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def coincidir(self, tipo, valor_esperado=None):
        token = self.obtener_token()
        if token and token.tipo == tipo and (valor_esperado is None or token.lexema == valor_esperado):
            self.index += 1
            return token
        
        # Generar error más descriptivo solo si no se encuentra el token
        if token:
            esperado = valor_esperado if valor_esperado else tipo
            recibido = token.lexema
            linea = token.linea
            columna = token.columna
            self.errores.append(f"Error sintáctico en L{linea} C{columna}: se esperaba '{esperado}', pero se obtuvo '{recibido}'")
        else:
            esperado = valor_esperado if valor_esperado else tipo
            self.errores.append(f"Error sintáctico: se esperaba '{esperado}', pero se llegó al final del archivo")
        return None

    def coincidir_opcional(self, tipo, valor_esperado=None):
        """Versión que no genera error si no encuentra el token"""
        token = self.obtener_token()
        if token and token.tipo == tipo and (valor_esperado is None or token.lexema == valor_esperado):
            self.index += 1
            return token
        return None

    def sincronizar(self, tokens_sincronizacion):
        """Avanza hasta encontrar un token de sincronización"""
        while self.index < len(self.tokens):
            token_actual = self.obtener_token()
            if token_actual and (token_actual.lexema in tokens_sincronizacion or token_actual.tipo in tokens_sincronizacion):
                break
            self.index += 1

    def parse(self):
        return self.parse_programa()

    def parse_programa(self):
        nodo = ASTNode("programa")
        token_main = self.coincidir("RESERVADA", "main")
        
        if not token_main:
            # Intentar recuperarse buscando 'main'
            self.sincronizar(["main"])
            if self.obtener_token() and self.obtener_token().lexema == "main":
                token_main = self.coincidir("RESERVADA", "main")
        
        brace_open = self.coincidir("SIMBOLO", "{")
        if not brace_open:
            # Intentar recuperarse buscando '{'
            self.sincronizar(["{"])
            if self.obtener_token() and self.obtener_token().lexema == "{":
                brace_open = self.coincidir("SIMBOLO", "{")

        # Continuar parseando el contenido aunque falte main o {
        lista_decl = self.parse_lista_declaracion()
        if lista_decl:
            nodo.agregar_hijo(lista_decl)
        
        # Intentar encontrar el cierre
        brace_close = self.coincidir_opcional("SIMBOLO", "}")
        if not brace_close and token_main:  # Solo reportar error si teníamos main
            pass  # No reportar error de } faltante para ser más permisivo
        
        return nodo
    
    def parse_lista_declaracion(self):
        nodo = ASTNode("lista_declaracion")
        
        while self.index < len(self.tokens):
            token_actual = self.obtener_token()
            
            # Salir si encontramos el cierre del bloque principal
            if token_actual and token_actual.lexema == "}":
                break
                
            decl = self.parse_declaracion()
            if decl:
                nodo.agregar_hijo(decl)
            else:
                # Si no se pudo parsear, avanzar un token para evitar bucle infinito
                if self.index < len(self.tokens):
                    token_actual = self.obtener_token()
                    if token_actual:
                        # Solo reportar error si no es un token de cierre
                        if token_actual.lexema != "}":
                            self.errores.append(f"Error sintáctico en L{token_actual.linea} C{token_actual.columna}: token inesperado '{token_actual.lexema}'")
                    self.index += 1
        
        return nodo

    def parse_declaracion(self):
        actual = self.obtener_token()
        if not actual:
            return None
            
        if actual.lexema in ["int", "float", "bool"]:
            return self.parse_declaracion_variable()
        elif actual.lexema in ["if", "while", "do", "cin", "cout"] or actual.tipo == "IDENTIFICADOR":
            return self.parse_sentencia()
        
        return None

    def parse_sentencia(self):
        actual = self.obtener_token()
        if actual is None:
            return None

        try:
            if actual.tipo == "IDENTIFICADOR":
                # Verifica si es un operador unario como sentencia
                siguiente = self.tokens[self.index + 1] if self.index + 1 < len(self.tokens) else None
                if siguiente and siguiente.tipo == "OPERADOR_ARIT" and siguiente.lexema in ["++", "--"]:
                    return self.parse_sentencia_unaria()
                elif siguiente and (siguiente.tipo == "ASIGNACION" or siguiente.lexema == "="):
                    return self.parse_asignacion()
                else:
                    # Es una expresión suelta (ej: y + 2;)
                    return self.parse_expresion_sentencia()
            elif actual.lexema == "cout":
                return self.parse_sent_out()
            elif actual.lexema == "cin":
                return self.parse_sent_in()
            elif actual.lexema == "if":
                return self.parse_seleccion()
            elif actual.lexema == "do":
                return self.parse_do_while()
            elif actual.lexema == "while":
                return self.parse_while()
        except Exception as e:
            if actual:
                self.errores.append(f"Error procesando sentencia en L{actual.linea} C{actual.columna}: {str(e)}")
            # Recuperación: sincronizar con tokens de inicio de sentencia o fin de bloque
            self.sincronizar([";", "if", "while", "do", "cin", "cout", "}", "else"])
            return None
        
        return None

    def parse_sentencia_unaria(self):
        nodo = ASTNode("unario")
        id_token = self.coincidir("IDENTIFICADOR")
        op_token = self.coincidir("OPERADOR_ARIT")
        valor_unario = +1 if op_token.lexema == "++" else -1
        nodo.agregar_hijo(ASTNode("id", id_token.lexema, id_token.linea, id_token.columna))
        nodo.agregar_hijo(ASTNode("op", valor_unario, op_token.linea, op_token.columna))
        self.coincidir_opcional("SIMBOLO", ";")
        return nodo
    
    def parse_expresion_sentencia(self):
        """Parsea una expresión suelta como sentencia (ej: y + 2;)"""
        nodo = ASTNode("expresion_sentencia")
        expr = self.parse_expresion()
        if expr:
            nodo.agregar_hijo(expr)
        self.coincidir_opcional("SIMBOLO", ";")
        return nodo

    def parse_asignacion(self):
        nodo = ASTNode("asignacion")
        id_token = self.coincidir("IDENTIFICADOR")
        if not id_token:
            return None

        nodo.agregar_hijo(ASTNode("id", id_token.lexema, id_token.linea, id_token.columna))

        asign_token = self.coincidir_opcional("ASIGNACION")
        if not asign_token:
            asign_token = self.coincidir_opcional("SIMBOLO", "=")
        if not asign_token:
            self.errores.append(f"Error en L{id_token.linea} C{id_token.columna + len(id_token.lexema)}: Se esperaba '=' después del identificador '{id_token.lexema}'")
            return nodo

        expr = self.parse_expresion()
        if expr:
            nodo.agregar_hijo(expr)
        else:
            self.errores.append(f"Error: Expresión no válida en asignación de '{id_token.lexema}'")

        # Cambia aquí:
        if not self.coincidir("SIMBOLO", ";"):
            self.errores.append("Error: Falta ';' al final de la sentencia")

        return nodo

    def parse_expresion(self):
        nodo = self.parse_expresion_simple()
        if not nodo:
            return None

        while True:
            token = self.obtener_token()
            if token and token.tipo in ["OPERADOR_REL", "OPERADOR_LOG"]:
                operador = self.coincidir(token.tipo)
                derecho = self.parse_expresion_simple()
                if not derecho:
                    self.errores.append(f"Error: Falta expresión después de operador '{operador.lexema}'")
                    break
                nuevo = ASTNode("op", operador.lexema)
                nuevo.agregar_hijo(nodo)
                nuevo.agregar_hijo(derecho)
                nodo = nuevo
            else:
                break
        return nodo

    def parse_sent_out(self):
        nodo = ASTNode("sent_out")
        
        cout_token = self.coincidir("RESERVADA", "cout")
        if not cout_token:
            return None

        # Agregar nodo para la palabra reservada 'cout'
        nodo.agregar_hijo(ASTNode("RESERVADA", cout_token.lexema, cout_token.linea, cout_token.columna))
        
        while True:
            operador = self.coincidir_opcional("OPERADOR_REL", "<<")
            if not operador:
                operador = self.coincidir_opcional("SIMBOLO", "<<")
            if not operador:
                break

            valor = self.obtener_token()
            if valor and valor.tipo in ["CADENA", "IDENTIFICADOR", "NUMERO_ENTERO", "NUMERO_REAL"]:
                self.index += 1
                nodo.agregar_hijo(ASTNode("id", valor.lexema, valor.linea, valor.columna))
            else:
                self.errores.append("Error: Valor no válido en cout después de '<<'")
                break

            siguiente = self.obtener_token()
            if not (siguiente and (
                (siguiente.tipo == "OPERADOR_REL" and siguiente.lexema == "<<") or
                (siguiente.tipo == "SIMBOLO" and siguiente.lexema == "<<")
            )):
                break

        semicolon = self.coincidir_opcional("SIMBOLO", ";")
        return nodo

    def parse_sent_in(self):
        nodo = ASTNode("sent_in")
        cin_token = self.coincidir("RESERVADA", "cin")
        
        if not cin_token:
            return None

        # Agregar nodo para la palabra reservada 'cin'
        nodo.agregar_hijo(ASTNode("RESERVADA", cin_token.lexema, cin_token.linea, cin_token.columna))
        
        operador = self.coincidir_opcional("OPERADOR_REL", ">>")
        if not operador:
            operador = self.coincidir_opcional("SIMBOLO", ">>")
            
        if not operador:
            self.errores.append("Error: Se esperaba '>>' después de 'cin'")
            return nodo
        
        id_token = self.coincidir("IDENTIFICADOR")
        if id_token:
            nodo.agregar_hijo(ASTNode("id", id_token.lexema, id_token.linea, id_token.columna))
        else:
            self.errores.append("Error: Se esperaba un identificador después de 'cin >>'")
        
        semicolon = self.coincidir_opcional("SIMBOLO", ";")
        
        return nodo

    def parse_seleccion(self):
        nodo = ASTNode("seleccion")
        if_token = self.coincidir("RESERVADA", "if")
        if not if_token:
            return None

        # Nodo para 'if'
        nodo.agregar_hijo(ASTNode("RESERVADA", if_token.lexema, if_token.linea, if_token.columna))

        # Forzar uso de paréntesis
        if not self.coincidir("SIMBOLO", "("):
            self.errores.append("Error: Se esperaba '(' después de 'if'")
            # Puedes intentar recuperarte aquí si quieres
            return None

        nodo_cond = self.parse_expresion()
        if not nodo_cond:
            self.errores.append("Error: Condición no válida en 'if'")
            return None

        if not self.coincidir("SIMBOLO", ")"):
            self.errores.append("Error: Se esperaba ')' después de la condición del 'if'")
            return None

        if not self.obtener_token() or self.obtener_token().lexema != "{":
            self.errores.append("Error: Se esperaba '{' después de la condición del 'if'")
            return None

        nodo.agregar_hijo(nodo_cond)

        sent_then = self.parse_bloque_sentencias()
        if sent_then and sent_then.hijos:
            nodo.agregar_hijo(sent_then)
        else:
            self.errores.append("Error: Se esperaba un bloque '{...}' después del 'if'")

        # Manejar ELSE opcional con llave
        if self.obtener_token() and self.obtener_token().lexema == "else":
            else_token = self.coincidir("RESERVADA", "else")
            nodo.agregar_hijo(ASTNode("RESERVADA", else_token.lexema, else_token.linea, else_token.columna))

            if not self.obtener_token() or self.obtener_token().lexema != "{":
                self.errores.append("Error: Se esperaba '{' después de 'else'")
                return nodo

            sent_else = self.parse_bloque_sentencias()
            if sent_else and sent_else.hijos:
                nodo.agregar_hijo(sent_else)
            else:
                self.errores.append("Error: Se esperaba un bloque '{...}' después del 'else'")

        return nodo

    def parse_while(self):
        nodo = ASTNode("while")
        while_token = self.coincidir("RESERVADA", "while")
        if not while_token:
            return None

        paren_open = self.coincidir_opcional("SIMBOLO", "(")
        if not paren_open:
            self.errores.append("Error: Se esperaba '(' después de 'while'")
            return None

        cond = self.parse_expresion()
        if cond: 
            nodo.agregar_hijo(cond)
        else:
            self.errores.append("Error: Condición no válida en 'while'")

        paren_close = self.coincidir_opcional("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'while'")

        sent = self.parse_bloque_sentencias()
        if sent:
            nodo.agregar_hijo(sent)

        return nodo
    
    def parse_do_while(self):
        nodo = ASTNode("do_while")
        do_token = self.coincidir("RESERVADA", "do")
        if not do_token:
            return None

        bloque = self.parse_bloque_sentencias()
        if bloque:
            nodo.agregar_hijo(bloque)
        else:
            self.errores.append("Error: Se esperaba un bloque '{...}' después de 'do'")
            return nodo

        if not self.coincidir("RESERVADA", "while"):
            self.errores.append("Error: Se esperaba 'while' después del bloque 'do'")
            return nodo

        if not self.coincidir("SIMBOLO", "("):
            self.errores.append("Error: Se esperaba '(' después de 'while'")
            return nodo

        cond = self.parse_expresion()
        if cond:
            nodo.agregar_hijo(cond)
        else:
            self.errores.append("Error: Condición no válida en 'do-while'")

        if not self.coincidir("SIMBOLO", ")"):
            self.errores.append("Error: Se esperaba ')' después de la condición del 'while'")

        if not self.coincidir("SIMBOLO", ";"):
            self.errores.append("Error: Se esperaba ';' al final de 'do-while'")

        return nodo

    def parse_declaracion_variable(self):
        nodo = ASTNode("declaracion_variable")
        tipo = self.coincidir("RESERVADA")
        if not tipo:
            return None

        # Agrega el nodo del tipo (int, float, bool)
        nodo.agregar_hijo(ASTNode("tipo", tipo.lexema, tipo.linea, tipo.columna))

        # Lista de identificadores
        nodo_ids = ASTNode("identificadores")
        id_token = self.coincidir("IDENTIFICADOR")
        if id_token:
            nodo_ids.agregar_hijo(ASTNode("id", id_token.lexema, id_token.linea, id_token.columna))
            while True:
                coma = self.coincidir_opcional("SIMBOLO", ",")
                if coma:
                    siguiente_id = self.coincidir("IDENTIFICADOR")
                    if siguiente_id:
                        nodo_ids.agregar_hijo(ASTNode("id", siguiente_id.lexema, siguiente_id.linea, siguiente_id.columna))
                    else:
                        self.errores.append("Error: Se esperaba un identificador después de ','")
                        break
                else:
                    break
            nodo.agregar_hijo(nodo_ids)
        else:
            self.errores.append(f"Error: Se esperaba un identificador después de '{tipo.lexema}'")

        # Punto y coma obligatorio
        if not self.coincidir("SIMBOLO", ";"):
            self.errores.append("Error: Falta ';' al final de la declaración de variable")
        return nodo  # <-- asegúrate que este return esté dentro de la función, no fuera

    def parse_expresion_simple(self):
        nodo = self.parse_termino()
        if not nodo:
            return None

        while True:
            token = self.obtener_token()
            if token and token.tipo == "OPERADOR_ARIT" and token.lexema in ["+", "-"]:
                operador = self.coincidir("OPERADOR_ARIT")
                derecho = self.parse_termino()
                if not derecho:
                    self.errores.append(f"Error: Operador '{operador.lexema}' sin operando derecho")
                    break
                nuevo = ASTNode("suma_op", operador.lexema)
                nuevo.agregar_hijo(nodo)
                nuevo.agregar_hijo(derecho)
                nodo = nuevo
            # Manejar operadores unarios ++ y --
            elif token and token.tipo == "OPERADOR_ARIT" and token.lexema in ["++", "--"]:
                operador = self.coincidir("OPERADOR_ARIT")
                valor_unario = +1 if operador.lexema == "++" else -1
                nuevo = ASTNode("unario_op", valor_unario)
                nuevo.agregar_hijo(nodo)
                nodo = nuevo
            else:
                break
        return nodo

    def parse_termino(self):
        nodo = self.parse_factor()
        if not nodo:
            return None

        while True:
            token = self.obtener_token()
            if token and token.tipo == "OPERADOR_ARIT" and token.lexema in ["*", "/", "%"]:
                operador = self.coincidir("OPERADOR_ARIT")
                derecho = self.parse_factor()
                if not derecho:
                    self.errores.append(f"Error: Operador '{operador.lexema}' sin operando derecho")
                    break
                
                nuevo = ASTNode("mult_op", operador.lexema)
                nuevo.agregar_hijo(nodo)
                nuevo.agregar_hijo(derecho)
                nodo = nuevo
            else:
                break
        return nodo

    def parse_factor(self):
        nodo = self.parse_componente()
        if not nodo:
            return None

        while True:
            token = self.obtener_token()
            if token and token.tipo == "OPERADOR_ARIT" and token.lexema == "^":
                operador = self.coincidir("OPERADOR_ARIT")
                derecho = self.parse_componente()
                if not derecho:
                    self.errores.append("Error: Se esperaba el exponente después de '^'")
                    break
                nuevo = ASTNode("pot_op", operador.lexema)
                nuevo.agregar_hijo(nodo)
                nuevo.agregar_hijo(derecho)
                nodo = nuevo
            else:
                break
        return nodo

    def parse_componente(self):
        token = self.obtener_token()
        if not token:
            return None

        if token.lexema == "(":
            self.coincidir("SIMBOLO", "(")
            nodo = self.parse_expresion()
            if not self.coincidir_opcional("SIMBOLO", ")"):
                self.errores.append("Error: Falta ')' después de la expresión")
            return nodo

        elif token.tipo in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR", "CADENA"]:
            self.index += 1
            return ASTNode(token.tipo, token.lexema, token.linea, token.columna)

        elif token.tipo == "RESERVADA" and token.lexema in ["true", "false"]:
            self.index += 1
            return ASTNode("bool", token.lexema, token.linea, token.columna)

        elif token.tipo == "OPERADOR_LOG" and token.lexema == "!":
            operador = self.coincidir("OPERADOR_LOG", "!")
            derecho = self.parse_componente()
            if not derecho:
                self.errores.append("Error: Falta operando después de '!'")
                return None
            nodo = ASTNode("op_logico", "!", operador.linea, operador.columna)
            nodo.agregar_hijo(derecho)
            return nodo

        return None

    def parse_bloque_sentencias(self):
        # Verificar si es un bloque con { } o una sola sentencia
        if self.obtener_token() and self.obtener_token().lexema == "{":
            self.coincidir("SIMBOLO", "{")
            nodo_bloque = ASTNode("bloque")
            
            while self.obtener_token() and self.obtener_token().lexema != "}":
                sent = self.parse_sentencia()
                if sent:
                    nodo_bloque.agregar_hijo(sent)
                else:
                    # Evitar bucle infinito
                    if self.index < len(self.tokens):
                        self.index += 1
            
            # Aquí: reporta error si no hay }
            if not self.coincidir_opcional("SIMBOLO", "}"):
                self.errores.append("Error: Falta '}' al final del bloque")
                self.sincronizar(["}"])
            
            return nodo_bloque
        else:
            # Bloque de una sola sentencia
            sent = self.parse_sentencia()
            if sent:
                nodo_bloque = ASTNode("bloque")
                nodo_bloque.agregar_hijo(sent)
                return nodo_bloque
            return None

def insertar_nodo(parent, nodo):
    item_id = tree.insert(
        parent,
        "end",
        text=nodo.tipo,
        values=(
            nodo.valor if nodo.valor else "",
            nodo.linea if nodo.linea is not None else "",
            nodo.columna if nodo.columna is not None else ""
        ),
        open=False
    )
    for hijo in nodo.hijos:
        insertar_nodo(item_id, hijo)