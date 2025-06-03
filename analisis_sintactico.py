class Token:
    def __init__(self, tipo, lexema, linea, columna):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna

    def __str__(self):
        return f"{self.tipo}('{self.lexema}') en L{self.linea} C{self.columna}"

class ASTNode:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
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
        
        # Generar error más descriptivo
        esperado = valor_esperado if valor_esperado else tipo
        recibido = token.lexema if token else 'EOF'
        linea = token.linea if token else -1
        columna = token.columna if token else -1
        self.errores.append(f"Error sintáctico en L{linea} C{columna}: se esperaba '{esperado}', pero se obtuvo '{recibido}'")
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
            if token_actual and token_actual.lexema in tokens_sincronizacion:
                break
            self.index += 1

    def parse(self):
        return self.parse_programa()

    def parse_programa(self):
        nodo = ASTNode("programa")
        token_main = self.coincidir("RESERVADA", "main")
        
        if not token_main:
            self.errores.append("Error: Se esperaba 'main' al inicio del programa")
            # Intentar recuperarse buscando 'main'
            self.sincronizar(["main"])
            if self.obtener_token() and self.obtener_token().lexema == "main":
                token_main = self.coincidir("RESERVADA", "main")
        
        brace_open = self.coincidir("SIMBOLO", "{")
        if not brace_open:
            self.errores.append("Error: Se esperaba '{' después de 'main'")
            # Intentar recuperarse buscando '{'
            self.sincronizar(["{"])
            if self.obtener_token() and self.obtener_token().lexema == "{":
                brace_open = self.coincidir("SIMBOLO", "{")

        if token_main or brace_open:  # Continuar si tenemos al menos uno
            lista_decl = self.parse_lista_declaracion()
            if lista_decl:
                nodo.agregar_hijo(lista_decl)
            
            brace_close = self.coincidir("SIMBOLO", "}")
            if not brace_close:
                self.errores.append("Error: Se esperaba '}' al final del programa")
        
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
                # Recuperación de errores mejorada
                if token_actual:
                    self.errores.append(f"Error sintáctico en L{token_actual.linea} C{token_actual.columna}: declaración o sentencia no válida '{token_actual.lexema}'")
                
                # Avanzar hasta encontrar un punto de sincronización
                self.sincronizar([';', '}', 'int', 'float', 'bool', 'if', 'while', 'do', 'cin', 'cout'])
                
                # Si encontramos ';', lo consumimos para continuar
                if self.obtener_token() and self.obtener_token().lexema == ';':
                    self.index += 1
                elif self.obtener_token() and self.obtener_token().lexema == '}':
                    break  # Salir si encontramos el cierre del bloque
        
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
                return self.parse_asignacion()
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
            self.errores.append(f"Error procesando sentencia en L{actual.linea} C{actual.columna}: {str(e)}")
            return None
        
        return None

    def parse_asignacion(self):
        nodo = ASTNode("asignacion")
        id_token = self.coincidir("IDENTIFICADOR")
        
        if id_token:
            nodo.agregar_hijo(ASTNode("id", id_token.lexema))
        else:
            return None

        asign_token = self.coincidir("ASIGNACION")
        if not asign_token:
            self.errores.append(f"Error en L{id_token.linea} C{id_token.columna + len(id_token.lexema)}: Se esperaba '=' después del identificador '{id_token.lexema}'")
            return nodo
        
        expr = self.parse_expresion()
        if expr:
            nodo.agregar_hijo(expr)
        else:
            self.errores.append(f"Error: Expresión no válida en asignación de '{id_token.lexema}'")

        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon:
            self.errores.append(f"Error: Falta ';' al final de la asignación de '{id_token.lexema}'")
        
        return nodo

    def parse_expresion(self):
        nodo = ASTNode("expresion")
        izquierda = self.parse_expresion_simple()

        if not izquierda:
            return None

        token = self.obtener_token()
        if token and token.tipo == "OPERADOR_REL":
            operador = self.coincidir("OPERADOR_REL")
            derecha = self.parse_expresion_simple()
            if not derecha:
                self.errores.append(f"Error: Se esperaba una expresión a la derecha del operador relacional '{operador.lexema}'")
                return None
            nodo_operador = ASTNode("rel_op", operador.lexema)
            nodo_operador.agregar_hijo(izquierda)
            nodo_operador.agregar_hijo(derecha)
            nodo.agregar_hijo(nodo_operador)
            return nodo
        else:
            nodo.agregar_hijo(izquierda)
            return nodo

    def parse_sent_out(self):
        nodo = ASTNode("sent_out")
        
        cout_token = self.coincidir("RESERVADA", "cout")
        if not cout_token:
            return None
        
        while True:
            operador = self.coincidir("OPERADOR_REL", "<<")
            if not operador:
                self.errores.append("Error: Se esperaba '<<' después de 'cout' o de una salida")
                break

            valor = self.obtener_token()
            if valor and valor.tipo in ["CADENA", "IDENTIFICADOR", "NUMERO_ENTERO", "NUMERO_REAL"]:
                self.index += 1
                nodo.agregar_hijo(ASTNode(valor.tipo, valor.lexema))
            else:
                self.errores.append("Error: Valor no válido en cout después de '<<'")
                break

            # Mirar si sigue otro <<, si no, salimos
            siguiente = self.obtener_token()
            if not (siguiente and siguiente.tipo == "OPERADOR_REL" and siguiente.lexema == "<<"):
                break

        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon:
            self.errores.append("Error: Falta ';' al final de cout")
        
        return nodo

    def parse_sent_in(self):
        nodo = ASTNode("sent_in")
        cin_token = self.coincidir("RESERVADA", "cin")
        
        if not cin_token:
            return None
            
        operador = self.coincidir("OPERADOR_REL", ">>")
        if not operador:
            self.errores.append("Error: Se esperaba '>>' después de 'cin'")
            return nodo
        
        id_token = self.coincidir("IDENTIFICADOR")
        if id_token:
            nodo.agregar_hijo(ASTNode("id", id_token.lexema))
        else:
            self.errores.append("Error: Se esperaba un identificador después de 'cin >>'")
        
        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon:
            self.errores.append("Error: Falta ';' al final de cin")
        
        return nodo

    def parse_seleccion(self):
        nodo = ASTNode("seleccion")
        if_token = self.coincidir("RESERVADA", "if")

        if not if_token:
            return None

        paren_open = self.coincidir("SIMBOLO", "(")
        if not paren_open:
            self.errores.append("Error: Se esperaba '(' después de 'if'")
            self.sincronizar([")", "then"])

        nodo_cond = self.parse_expresion()
        if not nodo_cond:
            self.errores.append("Error: Condición no válida en 'if'")
        else:
            nodo.agregar_hijo(nodo_cond)

        paren_close = self.coincidir("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'if'")
            self.sincronizar(["then"])

        then_token = self.coincidir("RESERVADA", "then")
        if not then_token:
            self.errores.append("Error: Se esperaba 'then' después de la condición del 'if'")
            self.sincronizar(["else", "end", "{", "if", "IDENTIFICADOR", "cin", "cout", "do", "while"])

        sent_then = self.parse_bloque_sentencias()
        if sent_then:
            nodo.agregar_hijo(sent_then)

        if self.obtener_token() and self.obtener_token().lexema == "else":
            self.coincidir("RESERVADA", "else")
            sent_else = self.parse_bloque_sentencias()
            if sent_else:
                nodo.agregar_hijo(sent_else)

        end_token = self.coincidir("RESERVADA", "end")
        if not end_token:
            self.errores.append("Error: Se esperaba 'end' al final de la estructura 'if'")
            self.sincronizar([";", "}"])

        return nodo

    def parse_do_while(self):
        nodo = ASTNode("do_while")
        do_token = self.coincidir("RESERVADA", "do")
        
        if not do_token:
            return None
        
        sent = self.parse_bloque_sentencias()
        if sent:
            nodo.agregar_hijo(sent)
        else:
            self.errores.append("Error: Cuerpo no válido en 'do'")

        while_token = self.coincidir("RESERVADA", "while")
        if not while_token:
            self.errores.append("Error: Se esperaba 'while' después del cuerpo de 'do'")
            self.sincronizar(["(", ";"])

        paren_open = self.coincidir("SIMBOLO", "(")
        if not paren_open:
            self.errores.append("Error: Se esperaba '(' después de 'while'")
            self.sincronizar([")"])

        cond = self.parse_expresion()
        if cond:
            nodo.agregar_hijo(cond)
        else:
            self.errores.append("Error: Condición no válida en 'do-while'")
            self.sincronizar([")"])

        paren_close = self.coincidir("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'while'")
            self.sincronizar([";"])

        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon:
            self.errores.append("Error: Falta ';' al final de 'do-while'")

        return nodo

    def parse_while(self):
        nodo = ASTNode("while")
        while_token = self.coincidir("RESERVADA", "while")
        if not while_token:
            return None

        paren_open = self.coincidir("SIMBOLO", "(")
        if not paren_open:
            self.errores.append("Error: Se esperaba '(' después de 'while'")
            self.sincronizar([")", "{", "IDENTIFICADOR", "if", "do", "while", "cin", "cout"])

        cond = self.parse_expresion()
        if cond:
            nodo.agregar_hijo(cond)
        else:
            self.errores.append("Error: Condición no válida en 'while'")
            self.sincronizar([")"])

        paren_close = self.coincidir("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'while'")
            self.sincronizar(["{", "if", "IDENTIFICADOR", "cin", "cout", "do", "while"])

        sent = self.parse_bloque_sentencias()
        if sent:
            nodo.agregar_hijo(sent)

        return nodo
    
    def parse_declaracion_variable(self):
        nodo = ASTNode("declaracion_variable")
        tipo = self.coincidir("RESERVADA")
        if tipo:
            nodo.agregar_hijo(ASTNode("tipo", tipo.lexema))
        
        # Soporte para lista de identificadores
        id_token = self.coincidir("IDENTIFICADOR")
        if id_token:
            nodo_id = ASTNode("identificador")
            nodo_id.agregar_hijo(ASTNode("id", id_token.lexema))
            
            # Aceptar múltiples identificadores separados por coma
            while True:
                coma = self.coincidir_opcional("SIMBOLO", ",")
                if coma:
                    siguiente_id = self.coincidir("IDENTIFICADOR")
                    if siguiente_id:
                        nodo_id.agregar_hijo(ASTNode("id", siguiente_id.lexema))
                    else:
                        self.errores.append("Error: Se esperaba un identificador después de ','")
                        break
                else:
                    break
            nodo.agregar_hijo(nodo_id)
        else:
            self.errores.append(f"Error: Se esperaba un identificador después de '{tipo.lexema}'" if tipo else "Error: Se esperaba un identificador")

        # Punto y coma
        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon:
            self.errores.append("Error: Falta ';' después de declaración de variable")
        
        return nodo if tipo else None

    def parse_expresion_simple(self):
        nodo = self.parse_termino()
        if not nodo:
            return None

        while True:
            token = self.obtener_token()
            if token and token.tipo == "OPERADOR_ARIT" and token.lexema in ["+", "-", "++", "--"]:
                operador = self.coincidir("OPERADOR_ARIT")
                derecho = self.parse_termino()
                if not derecho:
                    self.errores.append(f"Error: Operador '{operador.lexema}' sin operando derecho")
                    break
                nuevo = ASTNode("suma_op", operador.lexema)
                nuevo.agregar_hijo(nodo)
                nuevo.agregar_hijo(derecho)
                nodo = nuevo
            else:
                break
        return nodo

    def parse_termino(self):
        # Empezar con el primer factor
        nodo = self.parse_factor()
        if not nodo:
            return None

        # Procesar operadores de multiplicación y división de izquierda a derecha
        while True:
            token = self.obtener_token()
            if token and token.tipo == "OPERADOR_ARIT" and token.lexema in ["*", "/", "%"]:
                operador = self.coincidir("OPERADOR_ARIT")
                derecho = self.parse_factor()
                if not derecho:
                    self.errores.append(f"Error: Operador '{operador.lexema}' sin operando derecho")
                    break
                
                # CORRECCIÓN: Crear nuevo nodo y hacer que el nodo actual sea el hijo izquierdo
                nuevo = ASTNode("mult_op", operador.lexema)
                nuevo.agregar_hijo(nodo)        # El nodo actual se convierte en hijo izquierdo
                nuevo.agregar_hijo(derecho)     # El nuevo operando es hijo derecho
                nodo = nuevo                    # El nuevo nodo se convierte en el nodo actual
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
            if not self.coincidir("SIMBOLO", ")"):
                self.errores.append("Error: Falta ')' después de la expresión")
            return nodo

        elif token.tipo in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR", "CADENA"]:
            self.index += 1
            return ASTNode(token.tipo, token.lexema)

        elif token.tipo == "RESERVADA" and token.lexema in ["true", "false"]:
            self.index += 1
            return ASTNode("bool", token.lexema)

        elif token.tipo == "OPERADOR_LOG" and token.lexema == "!":
            operador = self.coincidir("OPERADOR_LOG", "!")
            derecho = self.parse_componente()
            if not derecho:
                self.errores.append("Error: Falta operando después de '!'")
                return None
            nodo = ASTNode("op_logico", "!")
            nodo.agregar_hijo(derecho)
            return nodo

        return None

    def parse_bloque_sentencias(self):
        # Verifica si comienza con '{'
        if self.obtener_token() and self.obtener_token().lexema == "{":
            self.coincidir("SIMBOLO", "{")
            nodo_bloque = ASTNode("bloque")
            while self.obtener_token() and self.obtener_token().lexema != "}":
                sent = self.parse_sentencia()
                if sent:
                    nodo_bloque.agregar_hijo(sent)
                else:
                    self.index += 1  # intentar seguir adelante
            self.coincidir("SIMBOLO", "}")
            return nodo_bloque
        else:
            return self.parse_sentencia()