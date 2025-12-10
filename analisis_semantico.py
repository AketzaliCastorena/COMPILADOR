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
        self.variables = {}  # Mapeo de variables a direcciones de memoria
        self.dir_counter = 0
    
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
    
    def obtener_direccion(self, var):
        """Obtiene o asigna dirección de memoria a una variable"""
        if var not in self.variables:
            self.variables[var] = self.dir_counter
            self.dir_counter += 1
        return self.variables[var]
    
    def generar_codigo_p(self):
        """Genera código P a partir del código de tres direcciones"""
        codigo_p = []

        # Añadir comentario identificador del generador (útil para confirmar versión en UI)
        codigo_p.append('; Generador: etiquetas lab/fjp/ujp (minusculas)')

        def es_numero(s):
            try:
                float(s)
                return True
            except Exception:
                return False

        # Pre-analizar para detectar temporales que solo se usan en condiciones
        temporales_en_condicion = set()
        temporales_usados_en_operaciones = set()
        
        # Primero, detectar temporales usados en otras operaciones (como AND, OR)
        for instruccion in self.codigo:
            inst = instruccion.strip()
            if '=' in inst:
                _, expresion = inst.split('=', 1)
                expresion = expresion.strip()
                # Si la expresión contiene un temporal (t0, t1, etc.)
                import re
                temporales_en_expr = re.findall(r'\bt\d+\b', expresion)
                temporales_usados_en_operaciones.update(temporales_en_expr)
        
        # Luego, detectar temporales que van directo a if
        for i, instruccion in enumerate(self.codigo):
            inst = instruccion.strip()
            # Detectar: temporal = comparación seguido de if not temporal
            if '=' in inst and i + 1 < len(self.codigo):
                next_inst = self.codigo[i + 1].strip()
                if next_inst.startswith('if not') or next_inst.startswith('if '):
                    destino = inst.split('=')[0].strip()
                    # Solo optimizar si NO se usa en otras operaciones
                    if destino.startswith('t') and destino not in temporales_usados_en_operaciones:
                        temporales_en_condicion.add(destino)

        # Traducción instrucción a instrucción manteniendo etiquetas simbólicas
        i = 0
        while i < len(self.codigo):
            instruccion = self.codigo[i]
            inst = instruccion.strip()
            inst = instruccion.strip()

            # Comentarios
            if inst.startswith('#'):
                codigo_p.append(f"; {inst[1:].strip()}")
                i += 1
                continue

            # DECLARE var tipo -> reservar dirección (no emite instrucción de máquina)
            if inst.startswith('DECLARE'):
                partes = inst.split()
                if len(partes) >= 2:
                    var = partes[1]
                    self.obtener_direccion(var)
                i += 1
                continue

            # READ var
            if inst.startswith('READ'):
                var = inst.split()[1]
                dir_var = self.obtener_direccion(var)
                codigo_p.append('rd')
                codigo_p.append(f'sto {dir_var}')
                i += 1
                continue

            # WRITE var o literal
            if inst.startswith('WRITE'):
                partes = inst.split(None, 1)
                if len(partes) >= 2:
                    valor = partes[1]
                    # Si es una cadena literal (empieza con comilla)
                    if valor.startswith('"') or valor.startswith("'"):
                        codigo_p.append(f'ldc {valor}')
                        codigo_p.append('wr')
                    # Si es un número literal
                    elif es_numero(valor):
                        codigo_p.append(f'ldc {valor}')
                        codigo_p.append('wr')
                    # Si es una variable
                    else:
                        dir_var = self.obtener_direccion(valor)
                        codigo_p.append(f'lod {dir_var}')
                        codigo_p.append('wr')
                i += 1
                continue

            # Etiqueta sintáctica (ej: L0:)
            if inst.endswith(':') and not '=' in inst:
                label = inst.replace(':', '').strip()
                # Emitir etiqueta en formato: lab L0
                codigo_p.append(f'lab {label}')
                i += 1
                continue

            # Salto incondicional
            if inst.startswith('goto'):
                label = inst.split()[1]
                codigo_p.append(f'ujp {label}')
                i += 1
                continue

            # if not <cond> goto <label>
            if inst.startswith('if not'):
                partes = inst.split()
                # formato esperado: if not <cond> goto <label>
                if len(partes) >= 5:
                    cond = partes[2]
                    label = partes[4]
                    # Si el temporal ya NO fue almacenado, no cargarlo
                    if cond not in temporales_en_condicion:
                        # Manejar literales numéricos y booleanos
                        if es_numero(cond):
                            codigo_p.append(f'ldc {cond}')
                        elif cond in ('True', 'true', 'False', 'false'):
                            # traducir booleanos a 1/0
                            val = '1' if cond.lower() == 'true' else '0'
                            codigo_p.append(f'ldc {val}')
                        else:
                            dir_cond = self.obtener_direccion(cond)
                            codigo_p.append(f'lod {dir_cond}')
                    codigo_p.append(f'fjp {label}')
                    i += 1
                    continue

            # if <cond> goto <label>  (forma alternativa)
            if inst.startswith('if') and 'not' not in inst:
                partes = inst.split()
                if len(partes) >= 4:
                    cond = partes[1]
                    label = partes[3]
                    if cond not in temporales_en_condicion:
                        if es_numero(cond):
                            codigo_p.append(f'ldc {cond}')
                        elif cond in ('True', 'true', 'False', 'false'):
                            val = '1' if cond.lower() == 'true' else '0'
                            codigo_p.append(f'ldc {val}')
                        else:
                            dir_cond = self.obtener_direccion(cond)
                            codigo_p.append(f'lod {dir_cond}')
                    # comparar con cero -> si igual a 0 entonces falso
                    codigo_p.append('ldc 0')
                    codigo_p.append('equ')
                    codigo_p.append(f'fjp {label}')
                    i += 1
                    continue

            # Asignaciones y operaciones
            if '=' in inst:
                destino, expresion = inst.split('=', 1)
                destino = destino.strip()
                expresion = expresion.strip()

                # Manejar valores booleanos (True/False)
                if expresion in ('True', 'False', 'true', 'false'):
                    dir_dest = self.obtener_direccion(destino)
                    valor = '1' if expresion.lower() == 'true' else '0'
                    codigo_p.append(f'ldc {valor}')
                    codigo_p.append(f'sto {dir_dest}')
                    i += 1
                    continue

                # caso constante simple
                if es_numero(expresion):
                    dir_dest = self.obtener_direccion(destino)
                    codigo_p.append(f'ldc {expresion}')
                    codigo_p.append(f'sto {dir_dest}')
                    i += 1
                    continue

                # operadores soportados
                operadores = {
                    '==': 'equ', '!=': 'neq', '<=': 'leq', '>=': 'geq',
                    '&&': 'and', '||': 'or',
                    '<': 'les', '>': 'grt',
                    '+': 'adi', '-': 'sbi', '*': 'mpi', '/': 'dvi', '%': 'mod', '**': 'pot'
                }

                encontrado = False
                # buscar operadores de mayor longitud primero
                for op in sorted(operadores.keys(), key=lambda x: -len(x)):
                    if f' {op} ' in expresion:
                        op1, op2 = map(str.strip, expresion.split(op, 1))
                        # cargar operandos
                        if es_numero(op1):
                            codigo_p.append(f'ldc {op1}')
                        else:
                            codigo_p.append(f'lod {self.obtener_direccion(op1)}')
                        if es_numero(op2):
                            codigo_p.append(f'ldc {op2}')
                        else:
                            codigo_p.append(f'lod {self.obtener_direccion(op2)}')

                        nem = operadores[op]
                        if nem == 'neq':
                            # Implementar != como equ + ldc 0 + equ (negación)
                            codigo_p.append('equ')
                            codigo_p.append('ldc 0')
                            codigo_p.append('equ')
                        else:
                            codigo_p.append(nem)

                        # Solo almacenar si NO es un temporal usado solo en condición
                        if destino not in temporales_en_condicion:
                            codigo_p.append(f'sto {self.obtener_direccion(destino)}')
                        encontrado = True
                        break

                if encontrado:
                    i += 1
                    continue

                # Asignación simple var = var
                codigo_p.append(f'lod {self.obtener_direccion(expresion)}')
                codigo_p.append(f'sto {self.obtener_direccion(destino)}')
                i += 1
                continue
            
            # Incrementar contador si no hubo continue
            i += 1

        # finalizar programa
        codigo_p.append('hlt')
        return codigo_p


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
            
            # Generar código P
            codigo_p = self.generador.generar_codigo_p()
            
            return self.tabla_simbolos, self.errores, self.advertencias, self.generador.obtener_codigo(), semantico_detalle, codigo_p
        except Exception as e:
            self.errores.append(f"Error crítico en análisis semántico: {str(e)}")
            return self.tabla_simbolos, self.errores, self.advertencias, [], [], []

    def recolectar_info_semantica(self, nodo, resultado):
        """Recorre el AST y recolecta información semántica por nodo"""
        if nodo is None:
            return
        
        # Si es una tupla (resultado de visitar_expresion), ignorarla
        if isinstance(nodo, tuple):
            return
        
        # Verificar que tiene atributos necesarios
        if not hasattr(nodo, 'tipo'):
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
        
        # Si es una tupla (resultado de visitar_expresion), no procesarla
        if isinstance(nodo, tuple):
            return None
        
        # Verificar que tenga atributo tipo
        if not hasattr(nodo, 'tipo'):
            return None
        
        metodo_nombre = f"visitar_{nodo.tipo}"
        metodo = getattr(self, metodo_nombre, self.visitar_generico)
        return metodo(nodo)
    
    def visitar_generico(self, nodo):
        """Visita genérica para nodos sin método específico"""
        for hijo in nodo.hijos:
            if not isinstance(hijo, tuple) and hasattr(hijo, 'tipo'):
                self.visitar(hijo)
        return None
    
    def visitar_programa(self, nodo):
        """Visita el nodo programa"""
        self.generador.agregar("# Inicio del programa")
        for hijo in nodo.hijos:
            if not isinstance(hijo, tuple) and hasattr(hijo, 'tipo'):
                self.visitar(hijo)
        self.generador.agregar("# Fin del programa")
        return None
    
    def visitar_lista_declaracion(self, nodo):
        """Visita lista de declaraciones"""
        for hijo in nodo.hijos:
            if not isinstance(hijo, tuple) and hasattr(hijo, 'tipo'):
                self.visitar(hijo)
        return None
    
    def visitar_declaracion_variable(self, nodo):
        """Visita declaración de variable"""
        # Primer hijo es el tipo
        if nodo.hijos and not isinstance(nodo.hijos[0], tuple) and hasattr(nodo.hijos[0], 'tipo') and nodo.hijos[0].tipo == "tipo":
            self.tipo_actual = nodo.hijos[0].valor
            
            # Segundo hijo es la lista de identificadores
            if len(nodo.hijos) > 1 and not isinstance(nodo.hijos[1], tuple) and hasattr(nodo.hijos[1], 'tipo') and nodo.hijos[1].tipo == "identificadores":
                for id_nodo in nodo.hijos[1].hijos:
                    if isinstance(id_nodo, tuple) or not hasattr(id_nodo, 'tipo'):
                        continue
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
        
        # Segundo hijo es la expresión (evaluar antes de verificar el símbolo)
        expr_nodo = nodo.hijos[1]
        tipo_expr, temp_expr = self.visitar_expresion(expr_nodo)
        
        # Si temp_expr es un valor numérico calculado, almacenarlo para visualización
        valor_asignado = None
        if isinstance(temp_expr, (int, float)):
            valor_asignado = temp_expr
        else:
            # Intentar evaluar el valor si es una constante simple
            valor_asignado = self.evaluar_valor_simple(expr_nodo)
        
        # Almacenar el valor calculado en el nodo para visualización (incluso si hay error)
        if valor_asignado is not None:
            nodo.valor_calculado = valor_asignado
        
        if simbolo is None:
            self.errores.append(
                f"Error semántico en L{id_nodo.linea} C{id_nodo.columna}: "
                f"Variable '{nombre_var}' no declarada"
            )
            # Establecer un tipo genérico para visualización
            nodo.tipo_semantico = "int" if isinstance(valor_asignado, int) else "float" if isinstance(valor_asignado, float) else "unknown"
            return None
        
        # Marcar como usada e inicializada
        self.tabla_simbolos.marcar_usado(nombre_var, id_nodo.linea)
        
        if tipo_expr is None:
            return None
        
        # Verificar compatibilidad de tipos
        if not self.tipos_compatibles(simbolo.tipo, tipo_expr):
            self.errores.append(
                f"Error semántico en L{id_nodo.linea} C{id_nodo.columna}: "
                f"Incompatibilidad de tipos: no se puede asignar '{tipo_expr}' a '{simbolo.tipo}'"
            )
        
        self.tabla_simbolos.marcar_inicializado(nombre_var, valor_asignado)
        
        # Almacenar información semántica en el nodo de asignación
        nodo.tipo_semantico = simbolo.tipo  # Usar el tipo del símbolo
        
        # Generar código intermedio
        if temp_expr is not None:
            self.generador.agregar(f"{nombre_var} = {temp_expr}")
        
        return simbolo.tipo
    
    def visitar_expresion(self, nodo):
        """Visita una expresión y retorna su tipo"""
        if nodo is None:
            return None, None
        
        # Casos base: literales
        if nodo.tipo == "NUMERO_ENTERO":
            nodo.tipo_semantico = "int"
            try:
                return "int", int(nodo.valor)
            except:
                return "int", nodo.valor
        elif nodo.tipo == "NUMERO_REAL":
            nodo.tipo_semantico = "float"
            try:
                return "float", float(nodo.valor)
            except:
                return "float", nodo.valor
        elif nodo.tipo == "bool":
            nodo.tipo_semantico = "bool"
            # Convertir el string "true"/"false" a booleano de Python
            valor_bool = nodo.valor.lower() == "true" if isinstance(nodo.valor, str) else bool(nodo.valor)
            return "bool", valor_bool
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
            
            # Almacenar el tipo semántico en el nodo
            nodo.tipo_semantico = simbolo.tipo
            
            # Siempre retornar el nombre de la variable para el código intermedio
            # (no optimizar sustituyendo por el valor, ya que la variable puede cambiar)
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
                
                # Si ambos operandos son enteros, truncar decimales del resultado
                if isinstance(valor_calculado, (int, float)) and not isinstance(valor_calculado, bool):
                    if tipo_izq == "int" and tipo_der == "int":
                        # Para operaciones entre enteros, tomar solo la parte entera (truncar)
                        valor_calculado = int(valor_calculado)
                    else:
                        # Para operaciones con floats, aplicar redondeo decimal
                        valor_calculado = self.generador.redondear(valor_calculado)
                
                # Almacenar el valor calculado en el nodo para visualización
                if valor_calculado is not None:
                    nodo.valor_calculado = valor_calculado
            
            # Evaluar operadores lógicos && y || - Bloque independiente para operadores lógicos
            if operador in ['&&', '||']:
                # Intentar evaluar si ambos operandos son valores booleanos o pueden convertirse
                izq_bool = None
                der_bool = None
                
                # Convertir operandos a booleano si es posible
                if isinstance(temp_izq, bool):
                    izq_bool = temp_izq
                elif isinstance(temp_izq, (int, float)):
                    izq_bool = bool(temp_izq)
                
                if isinstance(temp_der, bool):
                    der_bool = temp_der
                elif isinstance(temp_der, (int, float)):
                    der_bool = bool(temp_der)
                
                # Si pudimos obtener ambos valores booleanos, calcular el resultado
                if izq_bool is not None and der_bool is not None:
                    if operador == '&&':
                        valor_calculado = izq_bool and der_bool
                    elif operador == '||':
                        valor_calculado = izq_bool or der_bool
                    
                    # Almacenar el valor calculado en el nodo
                    if valor_calculado is not None:
                        nodo.valor_calculado = valor_calculado
        except Exception as e:
            pass
        
        # Determinar tipo resultante
        if nodo.tipo == "op" and operador in ["<", ">", "<=", ">=", "==", "!=", "&&", "||"]:
            # Operadores relacionales y lógicos retornan bool
            tipo_resultado = "bool"
        elif tipo_izq == "float" or tipo_der == "float":
            tipo_resultado = "float"
        elif tipo_izq == "int" and tipo_der == "int":
            # Si ambos son int pero el resultado calculado es decimal, el tipo es float
            if valor_calculado is not None and isinstance(valor_calculado, float) and valor_calculado != int(valor_calculado):
                tipo_resultado = "float"
            else:
                tipo_resultado = "int"
        else:
            self.errores.append(
                f"Error semántico: Operación '{operador}' con tipos incompatibles '{tipo_izq}' y '{tipo_der}'"
            )
            return None, None
        
        # Almacenar el tipo en el nodo para visualización en el árbol
        nodo.tipo_semantico = tipo_resultado
        
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
        """Visita operación unaria (++, --, -)"""
        if len(nodo.hijos) < 1:
            return None, None
        
        # Manejar operador unario negativo (-)
        if nodo.valor == "-":
            tipo_operando, temp_operando = self.visitar_expresion(nodo.hijos[0])
            
            if tipo_operando not in ["int", "float"]:
                self.errores.append(
                    f"Error semántico: Operador unario '-' requiere tipo numérico, se recibió '{tipo_operando}'"
                )
                return None, None
            
            # Si el operando es un número literal, retornar el valor negado directamente
            if isinstance(temp_operando, (int, float)):
                valor_negado = -temp_operando
                nodo.valor_calculado = valor_negado
                nodo.tipo_semantico = tipo_operando
                return tipo_operando, valor_negado
            
            # Si es una variable, generar código intermedio
            temp = self.generador.nuevo_temporal()
            self.generador.agregar(f"{temp} = 0 - {temp_operando}")
            nodo.tipo_semantico = tipo_operando
            return tipo_operando, temp
        
        # El resto del código es para ++ y --
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
        
        # Marcar como usada DOS VECES: una para leer el valor y otra para escribir
        # Esto simula x = x + 1 o x = x - 1
        self.tabla_simbolos.marcar_usado(id_nodo.valor, id_nodo.linea)  # Primera vez: lectura
        self.tabla_simbolos.marcar_usado(id_nodo.valor, id_nodo.linea)  # Segunda vez: escritura
        
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
            
            # Intentar calcular el valor si es posible
            valor_calculado = None
            if isinstance(temp, bool):
                valor_calculado = not temp
                nodo.valor_calculado = valor_calculado
            
            # Almacenar tipo semántico
            nodo.tipo_semantico = "bool"
            
            temp_resultado = self.generador.nuevo_temporal()
            self.generador.agregar(f"{temp_resultado} = !{temp}")
            
            # Si calculamos un valor, retornarlo
            if valor_calculado is not None:
                return "bool", valor_calculado
            
            return "bool", temp_resultado
        
        return None, None
    
    def visitar_seleccion(self, nodo):
        """Visita estructura if-else"""
        # El primer hijo después de la palabra reservada es la condición
        condicion_idx = 1 if nodo.hijos and not isinstance(nodo.hijos[0], tuple) and hasattr(nodo.hijos[0], 'tipo') and nodo.hijos[0].tipo == "RESERVADA" else 0
        
        if len(nodo.hijos) > condicion_idx:
            tipo_cond, temp_cond = self.visitar_expresion(nodo.hijos[condicion_idx])
            
            if tipo_cond and tipo_cond != "bool":
                self.advertencias.append(
                    f"Advertencia: La condición del 'if' debería ser de tipo 'bool', se recibió '{tipo_cond}'"
                )
            
            # Verificar si hay bloque else
            tiene_else = False
            if len(nodo.hijos) > condicion_idx + 2:
                else_idx = condicion_idx + 2
                if not isinstance(nodo.hijos[else_idx], tuple) and hasattr(nodo.hijos[else_idx], 'tipo') and nodo.hijos[else_idx].tipo == "RESERVADA":
                    else_idx += 1
                if len(nodo.hijos) > else_idx:
                    tiene_else = True
            
            # Generar código intermedio optimizado
            if tiene_else:
                # If con else: necesita label_else y label_fin
                label_else = self.generador.nueva_etiqueta()
                label_fin = self.generador.nueva_etiqueta()
                
                self.generador.agregar(f"if not {temp_cond} goto {label_else}")
                
                # Bloque then
                if len(nodo.hijos) > condicion_idx + 1:
                    self.visitar(nodo.hijos[condicion_idx + 1])
                
                self.generador.agregar(f"goto {label_fin}")
                self.generador.agregar(f"{label_else}:")
                
                # Bloque else
                else_idx = condicion_idx + 2
                if not isinstance(nodo.hijos[else_idx], tuple) and hasattr(nodo.hijos[else_idx], 'tipo') and nodo.hijos[else_idx].tipo == "RESERVADA":
                    else_idx += 1
                self.visitar(nodo.hijos[else_idx])
                
                self.generador.agregar(f"{label_fin}:")
            else:
                # If sin else: solo necesita label_fin
                label_fin = self.generador.nueva_etiqueta()
                
                self.generador.agregar(f"if not {temp_cond} goto {label_fin}")
                
                # Bloque then
                if len(nodo.hijos) > condicion_idx + 1:
                    self.visitar(nodo.hijos[condicion_idx + 1])
                
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
            if not isinstance(hijo, tuple) and hasattr(hijo, 'tipo') and hijo.tipo == "id":
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
            # Verificar que hijo no es una tupla y tiene atributo tipo
            if isinstance(hijo, tuple) or not hasattr(hijo, 'tipo'):
                continue
                
            if hijo.tipo == "RESERVADA" and hijo.valor in ["cout", "<<"]:
                # Ignorar palabras reservadas cout y <<
                continue
            elif hijo.tipo == "id":
                # Verificar si el valor empieza con comilla (cadena literal tokenizada como id)
                if hasattr(hijo, 'valor') and isinstance(hijo.valor, str) and hijo.valor.startswith('"'):
                    # Es una cadena literal
                    self.generador.agregar(f"WRITE {hijo.valor}")
                else:
                    # Es un identificador de variable
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
                # Generar WRITE con el valor
                self.generador.agregar(f"WRITE {hijo.valor}")
        
        return None
    
    def visitar_bloque(self, nodo):
        """Visita un bloque de sentencias"""
        for hijo in nodo.hijos:
            if not isinstance(hijo, tuple) and hasattr(hijo, 'tipo'):
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
