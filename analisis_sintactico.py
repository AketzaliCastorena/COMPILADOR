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

    def parse_declaracion_variable(self):
        nodo = ASTNode("declaracion_variable")
        tipo = self.coincidir("RESERVADA")
        if tipo:
            nodo.agregar_hijo(ASTNode("tipo", tipo.lexema))
        
        id_token = self.coincidir("IDENTIFICADOR")
        if id_token:
            nodo.agregar_hijo(ASTNode("id", id_token.lexema))
        elif tipo:  # Solo reportar error si el tipo fue válido
            self.errores.append(f"Error: Se esperaba un identificador después de '{tipo.lexema}'")
        
        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon and (tipo or id_token):
            self.errores.append("Error: Falta ';' después de declaración de variable")
        
        return nodo if (tipo or id_token) else None

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
        actual = self.obtener_token()
        
        if not actual:
            self.errores.append("Error: Se esperaba una expresión")
            return None
            
        if actual.tipo in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR"]:
            nodo.agregar_hijo(ASTNode(actual.tipo, actual.lexema))
            self.index += 1
            
            # Manejar operadores binarios
            while True:
                actual = self.obtener_token()
                if actual and actual.tipo in ["OPERADOR_ARIT", "OPERADOR_REL", "OPERADOR_LOG"]:
                    operador = self.coincidir(actual.tipo)
                    siguiente = self.obtener_token()
                    
                    if siguiente and siguiente.tipo in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR"]:
                        nodo_operacion = ASTNode("operador", operador.lexema)
                        nodo_operacion.agregar_hijo(nodo)
                        nodo_operacion.agregar_hijo(ASTNode(siguiente.tipo, siguiente.lexema))
                        self.index += 1
                        nodo = nodo_operacion
                    else:
                        self.errores.append(f"Error: Operador '{operador.lexema}' sin operando derecho")
                        break
                else:
                    break
            return nodo
        else:
            self.errores.append(f"Error en L{actual.linea} C{actual.columna}: Expresión no válida, se encontró '{actual.lexema}'")
            self.sincronizar([';', ')'])  # ← agregar esta línea
            return None

    def parse_sent_out(self):
        nodo = ASTNode("sent_out")
        cout_token = self.coincidir("RESERVADA", "cout")
        
        if not cout_token:
            return None
            
        operador = self.coincidir("OPERADOR_REL", "<<")
        if not operador:
            self.errores.append("Error: Se esperaba '<<' después de 'cout'")
            return nodo
        
        valor = self.obtener_token()
        if valor and valor.tipo in ["CADENA", "IDENTIFICADOR", "NUMERO_ENTERO", "NUMERO_REAL"]:
            self.index += 1
            nodo.agregar_hijo(ASTNode(valor.tipo, valor.lexema))
        else:
            self.errores.append("Error: Valor no válido en cout")
        
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
        
        nodo_cond = self.parse_expresion()
        if nodo_cond:
            nodo.agregar_hijo(nodo_cond)
        else:
            self.errores.append("Error: Condición no válida en 'if'")
        
        paren_close = self.coincidir("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'if'")
        
        then_token = self.coincidir("RESERVADA", "then")
        if not then_token:
            self.errores.append("Error: Se esperaba 'then' después de la condición del 'if'")
        
        sent_then = self.parse_sentencia()
        if sent_then:
            nodo.agregar_hijo(sent_then)
        
        # Verificar 'else' opcional
        if self.obtener_token() and self.obtener_token().lexema == "else":
            self.coincidir("RESERVADA", "else")
            sent_else = self.parse_sentencia()
            if sent_else:
                nodo.agregar_hijo(sent_else)
        
        end_token = self.coincidir("RESERVADA", "end")
        if not end_token:
            self.errores.append("Error: Se esperaba 'end' al final de la estructura 'if'")
        
        return nodo

    def parse_do_while(self):
        nodo = ASTNode("do_while")
        do_token = self.coincidir("RESERVADA", "do")
        
        if not do_token:
            return None
        
        sent = self.parse_sentencia()
        if sent:
            nodo.agregar_hijo(sent)
        
        while_token = self.coincidir("RESERVADA", "while")
        if not while_token:
            self.errores.append("Error: Se esperaba 'while' después del cuerpo de 'do'")
        
        paren_open = self.coincidir("SIMBOLO", "(")
        if not paren_open:
            self.errores.append("Error: Se esperaba '(' después de 'while'")
        
        cond = self.parse_expresion()
        if cond:
            nodo.agregar_hijo(cond)
        else:
            self.errores.append("Error: Condición no válida en 'do-while'")
        
        paren_close = self.coincidir("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'while'")
        
        semicolon = self.coincidir("SIMBOLO", ";")
        if not semicolon:
            self.errores.append("Error: Falta ';' al final de 'do-while'")
        
        return nodo

    def parse_while(self):
        """Método adicional para manejar while simple"""
        nodo = ASTNode("while")
        while_token = self.coincidir("RESERVADA", "while")
        
        if not while_token:
            return None
        
        paren_open = self.coincidir("SIMBOLO", "(")
        if not paren_open:
            self.errores.append("Error: Se esperaba '(' después de 'while'")
        
        cond = self.parse_expresion()
        if cond:
            nodo.agregar_hijo(cond)
        else:
            self.errores.append("Error: Condición no válida en 'while'")
        
        paren_close = self.coincidir("SIMBOLO", ")")
        if not paren_close:
            self.errores.append("Error: Se esperaba ')' después de la condición del 'while'")
        
        sent = self.parse_sentencia()
        if sent:
            nodo.agregar_hijo(sent)
        
        return nodo