"""
Analizador Semántico - Fase 3
Implementa:
- Tabla de símbolos (hash)
- Verificación de tipos
- Análisis de declaraciones y uso de variables
- Generación de código intermedio (tres direcciones)
"""

class Simbolo:
    """Representa un símbolo en la tabla de símbolos"""
    def __init__(self, nombre, tipo, linea, columna, inicializado=False, valor=None, registro=None):
        self.nombre = nombre
        self.tipo = tipo  # 'int', 'float', 'bool'
        self.linea = linea
        self.columna = columna
        self.inicializado = inicializado
        self.usado = False
        self.valor = valor
        self.registro = registro  # Número de registro en la tabla hash
        self.lineas_uso = []  # Lista de líneas donde se usa la variable

class TablaSimbolos:
    """Tabla de símbolos implementada con hash"""
    def __init__(self, tamano=100):
        self.tamano = tamano
        self.tabla = [[] for _ in range(tamano)]
        self.simbolos_lista = []  # Para mantener orden de inserción
    
    def hash(self, nombre):
        """Función hash simple: suma de valores ASCII módulo tamaño"""
        return sum(ord(c) for c in nombre) % self.tamano
    
    def insertar(self, nombre, tipo, linea, columna, inicializado=False, valor=None):
        """Inserta un símbolo en la tabla"""
        indice = self.hash(nombre)
        
        # Verificar si ya existe en ese bucket
        for simbolo in self.tabla[indice]:
            if simbolo.nombre == nombre:
                return False, f"Error semántico en L{linea} C{columna}: Variable '{nombre}' ya declarada en L{simbolo.linea} C{simbolo.columna}"
        
        # Insertar nuevo símbolo
        simbolo = Simbolo(nombre, tipo, linea, columna, inicializado, valor=valor, registro=indice)
        self.tabla[indice].append(simbolo)
        self.simbolos_lista.append(simbolo)
        return True, None
    
    def buscar(self, nombre):
        """Busca un símbolo en la tabla"""
        indice = self.hash(nombre)
        for simbolo in self.tabla[indice]:
            if simbolo.nombre == nombre:
                return simbolo
        return None
    
    def marcar_usado(self, nombre, linea=None):
        """Marca una variable como usada y registra la línea (permite duplicados)"""
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo.usado = True
            if linea is not None:
                simbolo.lineas_uso.append(linea)
    
    def marcar_inicializado(self, nombre, valor=None):
        """Marca una variable como inicializada y opcionalmente asigna un valor"""
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo.inicializado = True
            if valor is not None:
                simbolo.valor = valor
    
    def obtener_simbolos(self):
        """Retorna lista de todos los símbolos"""
        return self.simbolos_lista
    
    def obtener_tabla_visual(self):
        """Retorna representación visual de la tabla hash con información detallada"""
        resultado = []
        contador = 0
        for i, bucket in enumerate(self.tabla):
            if bucket:
                for simbolo in bucket:
                    # Recolectar líneas donde se usa y ordenarlas
                    lineas_ordenadas = sorted(simbolo.lineas_uso) if simbolo.lineas_uso else [simbolo.linea]
                    lineas_uso = ",".join(map(str, lineas_ordenadas))
                    resultado.append({
                        'identificador': simbolo.nombre,
                        'registro': contador,
                        'valor': simbolo.valor if simbolo.valor is not None else '<input>',
                        'tipo_dato': simbolo.tipo,
                        'ambito': 'Global',  # Por ahora todos son globales
                        'lineas': lineas_uso,
                        'indice_hash': i,
                        'inicializado': simbolo.inicializado,
                        'usado': simbolo.usado
                    })
                    contador += 1
        return resultado
    
class GeneradorCodigoIntermedio:
    """Genera código de tres direcciones"""
    def __init__(self):
        self.codigo = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def nuevo_temporal(self):
        """Genera un nuevo temporal"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def nueva_etiqueta(self):
        """Genera una nueva etiqueta"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def agregar(self, instruccion):
        """Agrega una instrucción al código intermedio"""
        self.codigo.append(instruccion)
        
    def redondear(self, valor, decimales=2):
        """Redondea los números flotantes a un número fijo de decimales"""
        if isinstance(valor, float):
            return round(valor, decimales)
        return valor
    
    def obtener_codigo(self):
        """Retorna el código generado"""
        return self.codigo


class AnalizadorSemantico:
    """Analizador semántico que recorre el AST y verifica reglas semánticas"""
    def __init__(self, ast):
        self.ast = ast
        self.tabla_simbolos = TablaSimbolos()
        self.errores = []
        self.advertencias = []
        self.generador = GeneradorCodigoIntermedio()
        self.tipo_actual = None  # Para tracking del tipo en declaraciones
    
    def analizar(self):
        """Ejecuta el análisis semántico completo"""
        try:
            self.visitar(self.ast)
             # Verificar variables no usadas
            for simbolo in self.tabla_simbolos.obtener_simbolos():
                if not simbolo.usado:
                    self.advertencias.append(
                        f"Advertencia en L{simbolo.linea} C{simbolo.columna}: "
                        f"Variable '{simbolo.nombre}' declarada pero no usada"
                    )
            # Recolectar información semántica detallada
            semantico_detalle = []
            self.recolectar_info_semantica(self.ast, semantico_detalle)
            return self.tabla_simbolos, self.errores, self.advertencias, self.generador.obtener_codigo(), semantico_detalle
        except Exception as e:
            self.errores.append(f"Error crítico en análisis semántico: {str(e)}")
            return self.tabla_simbolos, self.errores, self.advertencias, [], []

    def recolectar_info_semantica(self, nodo, resultado):
        """Recorre el AST y recolecta información semántica por nodo"""
        if nodo is None:
            return
        # Determinar tipo semántico y valor
        tipo_sem = getattr(nodo, 'tipo_semantico', None)
        valor = getattr(nodo, 'valor_semantico', None)
        
        # Si no existen, intentar deducir
        if tipo_sem is None and hasattr(nodo, 'tipo'):
            tipo_sem = nodo.tipo
        if valor is None and hasattr(nodo, 'valor'):
            valor = nodo.valor
        
        # Si el nodo tiene un valor calculado de una operación, mostrarlo
        if hasattr(nodo, 'valor_calculado'):
            valor_calc = nodo.valor_calculado
            # Formatear el valor calculado
            if isinstance(valor_calc, bool):
                valor_calc_str = str(valor_calc).lower()
            elif isinstance(valor_calc, float):
                # Mostrar sin decimales si es un número entero
                if valor_calc == int(valor_calc):
                    valor_calc_str = str(int(valor_calc))
                else:
                    valor_calc_str = str(valor_calc)
            else:
                valor_calc_str = str(valor_calc)
            valor = f"{valor} ({valor_calc_str})"
        
        resultado.append({
            'nodo': nodo.tipo,
            'valor': valor,
            'tipo_semantico': tipo_sem,
            'linea': getattr(nodo, 'linea', ''),
            'columna': getattr(nodo, 'columna', '')
        })
        for hijo in getattr(nodo, 'hijos', []):
            self.recolectar_info_semantica(hijo, resultado)
    
    def visitar(self, nodo):
        """Visita un nodo del AST según su tipo"""
        if nodo is None:
            return None
        
        metodo_nombre = f"visitar_{nodo.tipo}"
        metodo = getattr(self, metodo_nombre, self.visitar_generico)
        return metodo(nodo)
    
    def visitar_generico(self, nodo):
        """Visita genérica para nodos sin método específico"""
        for hijo in nodo.hijos:
            self.visitar(hijo)
        return None
    
    def visitar_programa(self, nodo):
        """Visita el nodo programa"""
        self.generador.agregar("# Inicio del programa")
        for hijo in nodo.hijos:
            self.visitar(hijo)
        self.generador.agregar("# Fin del programa")
        return None
    
    def visitar_lista_declaracion(self, nodo):
        """Visita lista de declaraciones"""
        for hijo in nodo.hijos:
            self.visitar(hijo)
        return None
    
    def visitar_declaracion_variable(self, nodo):
        """Visita declaración de variable"""
        # Primer hijo es el tipo
        if nodo.hijos and nodo.hijos[0].tipo == "tipo":
            self.tipo_actual = nodo.hijos[0].valor
            
            # Segundo hijo es la lista de identificadores
            if len(nodo.hijos) > 1 and nodo.hijos[1].tipo == "identificadores":
                for id_nodo in nodo.hijos[1].hijos:
                    if id_nodo.tipo == "id":
                        exito, error = self.tabla_simbolos.insertar(
                            id_nodo.valor,
                            self.tipo_actual,
                            id_nodo.linea,
                            id_nodo.columna,
                            inicializado=False
                        )
                        if not exito:
                            self.errores.append(error)
                        else:
                            # Agregar línea de declaración
                            simbolo = self.tabla_simbolos.buscar(id_nodo.valor)
                            if simbolo:
                                simbolo.lineas_uso.append(id_nodo.linea)
                            # Generar código intermedio para declaración
                            self.generador.agregar(f"DECLARE {id_nodo.valor} {self.tipo_actual}")
        
        return None
    
    def visitar_asignacion(self, nodo):
        """Visita asignación"""
        if len(nodo.hijos) < 2:
            return None
        
        # Primer hijo es el identificador
        id_nodo = nodo.hijos[0]
        if id_nodo.tipo != "id":
            return None
        
        nombre_var = id_nodo.valor
        simbolo = self.tabla_simbolos.buscar(nombre_var)
        
        if simbolo is None:
            self.errores.append(
                f"Error semántico en L{id_nodo.linea} C{id_nodo.columna}: "
                f"Variable '{nombre_var}' no declarada"
            )
            return None
        
        # Marcar como usada e inicializada
        self.tabla_simbolos.marcar_usado(nombre_var, id_nodo.linea)
        
        # Segundo hijo es la expresión
        expr_nodo = nodo.hijos[1]
        tipo_expr, temp_expr = self.visitar_expresion(expr_nodo)
        
        if tipo_expr is None:
            return None
        
        # Verificar compatibilidad de tipos
        if not self.tipos_compatibles(simbolo.tipo, tipo_expr):
            self.errores.append(
                f"Error semántico en L{id_nodo.linea} C{id_nodo.columna}: "
                f"Incompatibilidad de tipos: no se puede asignar '{tipo_expr}' a '{simbolo.tipo}'"
            )
        
        # Si temp_expr es un valor numérico calculado, usarlo como valor
        valor_asignado = None
        if isinstance(temp_expr, (int, float)):
            valor_asignado = temp_expr
        else:
            # Intentar evaluar el valor si es una constante simple
            valor_asignado = self.evaluar_valor_simple(expr_nodo)
        
        self.tabla_simbolos.marcar_inicializado(nombre_var, valor_asignado)
        
        # Generar código intermedio
        if temp_expr:
            self.generador.agregar(f"{nombre_var} = {temp_expr}")
        
        return simbolo.tipo
    
    def visitar_expresion(self, nodo):
        """Visita una expresión y retorna su tipo"""
        if nodo is None:
            return None, None
        
        # Casos base: literales
        if nodo.tipo == "NUMERO_ENTERO":
            try:
                return "int", int(nodo.valor)
            except:
                return "int", nodo.valor
        elif nodo.tipo == "NUMERO_REAL":
            try:
                return "float", float(nodo.valor)
            except:
                return "float", nodo.valor
        elif nodo.tipo == "bool":
            return "bool", nodo.valor
        elif nodo.tipo == "id" or nodo.tipo == "IDENTIFICADOR":
            # Verificar que la variable exista
            simbolo = self.tabla_simbolos.buscar(nodo.valor)
            if simbolo is None:
                self.errores.append(
                    f"Error semántico en L{nodo.linea} C{nodo.columna}: "
                    f"Variable '{nodo.valor}' no declarada"
                )
                return None, None
            
            # Verificar que esté inicializada
            if not simbolo.inicializado:
                self.advertencias.append(
                    f"Advertencia en L{nodo.linea} C{nodo.columna}: "
                    f"Variable '{nodo.valor}' puede no estar inicializada"
                )
            
            self.tabla_simbolos.marcar_usado(nodo.valor, nodo.linea)
            
            # Si la variable tiene un valor conocido, retornarlo para cálculos
            if simbolo.valor is not None and isinstance(simbolo.valor, (int, float)):
                return simbolo.tipo, simbolo.valor
            
            return simbolo.tipo, nodo.valor
        
        # Operadores binarios
        elif nodo.tipo in ["suma_op", "mult_op", "pot_op", "op"]:
            return self.visitar_operacion_binaria(nodo)
        
        # Operador unario
        elif nodo.tipo in ["unario_op", "unario"]:
            return self.visitar_operacion_unaria(nodo)
        
        # Operador lógico
        elif nodo.tipo == "op_logico":
            return self.visitar_operacion_logica(nodo)
        
        # Recursivo para otros nodos
        else:
            for hijo in nodo.hijos:
                resultado = self.visitar_expresion(hijo)
                if resultado[0] is not None:
                    return resultado
        
        return None, None
    
    def visitar_operacion_binaria(self, nodo):
        """Visita operación binaria y calcula el valor si es posible"""
        if len(nodo.hijos) < 2:
            return None, None
        
        tipo_izq, temp_izq = self.visitar_expresion(nodo.hijos[0])
        tipo_der, temp_der = self.visitar_expresion(nodo.hijos[1])
        
        if tipo_izq is None or tipo_der is None:
            return None, None
        
        operador = nodo.valor
        
        # Intentar evaluar el valor si ambos operandos son literales
        valor_calculado = None
        try:
            if isinstance(temp_izq, (int, float)) and isinstance(temp_der, (int, float)):
                if operador == '+':
                    valor_calculado = temp_izq + temp_der
                elif operador == '-':
                    valor_calculado = temp_izq - temp_der
                elif operador == '*':
                    valor_calculado = temp_izq * temp_der
                elif operador == '/':
                    valor_calculado = temp_izq / temp_der if temp_der != 0 else None
                valor_calculado = self.generador.redondear(valor_calculado)
            elif operador == '<':
                    valor_calculado = temp_izq < temp_der
            elif operador == '>':
                    valor_calculado = temp_izq > temp_der
            elif operador == '<=':
                    valor_calculado = temp_izq <= temp_der
            elif operador == '>=':
                    valor_calculado = temp_izq >= temp_der
            elif operador == '==':
                    valor_calculado = temp_izq == temp_der
            elif operador == '!=':
                    valor_calculado = temp_izq != temp_der
                
                # Almacenar el valor calculado en el nodo para visualización
            if valor_calculado is not None:
                    nodo.valor_calculado = valor_calculado
                    # Debug: imprimir el cálculo
                    print(f"DEBUG: {temp_izq} {operador} {temp_der} = {valor_calculado}")
        except Exception as e:
            print(f"ERROR en cálculo: {e}")
            pass
        
        # Determinar tipo resultante
        if nodo.tipo == "op" and operador in ["<", ">", "<=", ">=", "==", "!=", "&&", "||"]:
            # Operadores relacionales y lógicos retornan bool
            tipo_resultado = "bool"
        elif tipo_izq == "float" or tipo_der == "float":
            tipo_resultado = "float"
        elif tipo_izq == "int" and tipo_der == "int":
            tipo_resultado = "int"
        else:
            self.errores.append(
                f"Error semántico: Operación '{operador}' con tipos incompatibles '{tipo_izq}' y '{tipo_der}'"
            )
            return None, None
        
        # Generar código intermedio
        temp = self.generador.nuevo_temporal()
        self.generador.agregar(f"{temp} = {temp_izq} {operador} {temp_der}")
        
        # Si calculamos un valor, usarlo en lugar del temporal
        if valor_calculado is not None:
            return tipo_resultado, valor_calculado
        
        return tipo_resultado, temp
    
    def visitar_unario(self, nodo):
        """Visita sentencia unaria como y++ o y-- (cuando aparece como sentencia completa)"""
        return self.visitar_operacion_unaria(nodo)
    
    def visitar_expresion_sentencia(self, nodo):
        """Visita una expresión suelta como sentencia (ej: y + 2;)"""
        if nodo.hijos:
            self.visitar_expresion(nodo.hijos[0])
        return None
    
    def visitar_operacion_unaria(self, nodo):
        """Visita operación unaria (++, --)"""
        if len(nodo.hijos) < 1:
            return None, None
        
        # El primer hijo debe ser un identificador
        id_nodo = nodo.hijos[0]
        if id_nodo.tipo != "id":
            return None, None
        
        simbolo = self.tabla_simbolos.buscar(id_nodo.valor)
        if simbolo is None:
            self.errores.append(
                f"Error semántico en L{id_nodo.linea} C{id_nodo.columna}: "
                f"Variable '{id_nodo.valor}' no declarada"
            )
            return None, None
        
        if simbolo.tipo not in ["int", "float"]:
            self.errores.append(
                f"Error semántico en L{id_nodo.linea} C{id_nodo.columna}: "
                f"Operador unario solo aplica a tipos numéricos, no a '{simbolo.tipo}'"
            )
            return None, None
        
        self.tabla_simbolos.marcar_usado(id_nodo.valor, id_nodo.linea)
        
        # Generar código intermedio
        operador = "++" if nodo.valor == 1 or len(nodo.hijos) > 1 and nodo.hijos[1].valor == 1 else "--"
        valor_cambio = 1 if nodo.valor == 1 else -1
        temp = self.generador.nuevo_temporal()
        self.generador.agregar(f"{temp} = {id_nodo.valor} + {valor_cambio}")
        self.generador.agregar(f"{id_nodo.valor} = {temp}")
        
        return simbolo.tipo, id_nodo.valor
    
    def visitar_operacion_logica(self, nodo):
        """Visita operación lógica"""
        if nodo.valor == "!" and len(nodo.hijos) >= 1:
            # Operador NOT unario
            tipo, temp = self.visitar_expresion(nodo.hijos[0])
            if tipo != "bool":
                self.errores.append(
                    f"Error semántico: Operador '!' requiere tipo 'bool', se recibió '{tipo}'"
                )
                return None, None
            
            temp_resultado = self.generador.nuevo_temporal()
            self.generador.agregar(f"{temp_resultado} = !{temp}")
            return "bool", temp_resultado
        
        return None, None
    
    def visitar_seleccion(self, nodo):
        """Visita estructura if-else"""
        # El primer hijo después de la palabra reservada es la condición
        condicion_idx = 1 if nodo.hijos and nodo.hijos[0].tipo == "RESERVADA" else 0
        
        if len(nodo.hijos) > condicion_idx:
            tipo_cond, temp_cond = self.visitar_expresion(nodo.hijos[condicion_idx])
            
            if tipo_cond and tipo_cond != "bool":
                self.advertencias.append(
                    f"Advertencia: La condición del 'if' debería ser de tipo 'bool', se recibió '{tipo_cond}'"
                )
            
            # Generar código intermedio
            label_else = self.generador.nueva_etiqueta()
            label_fin = self.generador.nueva_etiqueta()
            
            self.generador.agregar(f"if not {temp_cond} goto {label_else}")
            
            # Bloque then
            if len(nodo.hijos) > condicion_idx + 1:
                self.visitar(nodo.hijos[condicion_idx + 1])
            
            self.generador.agregar(f"goto {label_fin}")
            self.generador.agregar(f"{label_else}:")
            
            # Bloque else (si existe)
            if len(nodo.hijos) > condicion_idx + 2:
                # Verificar si hay un nodo RESERVADA "else"
                else_idx = condicion_idx + 2
                if nodo.hijos[else_idx].tipo == "RESERVADA":
                    else_idx += 1
                if len(nodo.hijos) > else_idx:
                    self.visitar(nodo.hijos[else_idx])
            
            self.generador.agregar(f"{label_fin}:")
        
        return None
    
    def visitar_while(self, nodo):
        """Visita estructura while"""
        label_inicio = self.generador.nueva_etiqueta()
        label_fin = self.generador.nueva_etiqueta()
        
        self.generador.agregar(f"{label_inicio}:")
        
        # Condición
        if len(nodo.hijos) > 0:
            tipo_cond, temp_cond = self.visitar_expresion(nodo.hijos[0])
            
            if tipo_cond and tipo_cond != "bool":
                self.advertencias.append(
                    f"Advertencia: La condición del 'while' debería ser de tipo 'bool', se recibió '{tipo_cond}'"
                )
            
            self.generador.agregar(f"if not {temp_cond} goto {label_fin}")
        
        # Cuerpo
        if len(nodo.hijos) > 1:
            self.visitar(nodo.hijos[1])
        
        self.generador.agregar(f"goto {label_inicio}")
        self.generador.agregar(f"{label_fin}:")
        
        return None
    
    def visitar_do_while(self, nodo):
        """Visita estructura do-while"""
        label_inicio = self.generador.nueva_etiqueta()
        
        self.generador.agregar(f"{label_inicio}:")
        
        # Cuerpo
        if len(nodo.hijos) > 0:
            self.visitar(nodo.hijos[0])
        
        # Condición
        if len(nodo.hijos) > 1:
            tipo_cond, temp_cond = self.visitar_expresion(nodo.hijos[1])
            
            if tipo_cond and tipo_cond != "bool":
                self.advertencias.append(
                    f"Advertencia: La condición del 'do-while' debería ser de tipo 'bool', se recibió '{tipo_cond}'"
                )
            
            self.generador.agregar(f"if {temp_cond} goto {label_inicio}")
        
        return None
    
    def visitar_sent_in(self, nodo):
        """Visita sentencia cin (entrada)"""
        # Buscar el identificador
        for hijo in nodo.hijos:
            if hijo.tipo == "id":
                simbolo = self.tabla_simbolos.buscar(hijo.valor)
                if simbolo is None:
                    self.errores.append(
                        f"Error semántico en L{hijo.linea} C{hijo.columna}: "
                        f"Variable '{hijo.valor}' no declarada"
                    )
                else:
                    self.tabla_simbolos.marcar_usado(hijo.valor, hijo.linea)
                    self.tabla_simbolos.marcar_inicializado(hijo.valor, "<input>")
                    self.generador.agregar(f"READ {hijo.valor}")
        
        return None
    
    def visitar_sent_out(self, nodo):
        """Visita sentencia cout (salida)"""
        # Visitar todos los identificadores o valores a imprimir
        for hijo in nodo.hijos:
            if hijo.tipo == "id":
                simbolo = self.tabla_simbolos.buscar(hijo.valor)
                if simbolo is None:
                    self.errores.append(
                        f"Error semántico en L{hijo.linea} C{hijo.columna}: "
                        f"Variable '{hijo.valor}' no declarada"
                    )
                else:
                    if not simbolo.inicializado:
                        self.advertencias.append(
                            f"Advertencia en L{hijo.linea} C{hijo.columna}: "
                            f"Variable '{hijo.valor}' puede no estar inicializada"
                        )
                    self.tabla_simbolos.marcar_usado(hijo.valor, hijo.linea)
                    self.generador.agregar(f"WRITE {hijo.valor}")
            elif hijo.tipo in ["NUMERO_ENTERO", "NUMERO_REAL", "CADENA"]:
                self.generador.agregar(f"WRITE {hijo.valor}")
        
        return None
    
    def visitar_bloque(self, nodo):
        """Visita un bloque de sentencias"""
        for hijo in nodo.hijos:
            self.visitar(hijo)
        return None
    
    def evaluar_valor_simple(self, nodo):
        """Intenta evaluar un valor simple (número literal)"""
        if nodo is None:
            return None
        
        if nodo.tipo == "NUMERO_ENTERO":
            try:
                return int(nodo.valor)
            except:
                return nodo.valor
        elif nodo.tipo == "NUMERO_REAL":
            try:
                return float(nodo.valor)
            except:
                return nodo.valor
        elif nodo.tipo == "bool":
            return nodo.valor
        else:
            # Para expresiones complejas, retornar None
            return None
    
    def tipos_compatibles(self, tipo1, tipo2):
        """Verifica si dos tipos son compatibles para asignación"""
        if tipo1 == tipo2:
            return True
        # float puede recibir int
        if tipo1 == "float" and tipo2 == "int":
            return True
        return False
