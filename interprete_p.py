"""
Intérprete de Código P (P-code)
Ejecuta las instrucciones generadas por el compilador
"""

class InterpreteP:
    def __init__(self):
        self.memoria = [0] * 1000  # Memoria para variables (1000 posiciones)
        self.pila = []              # Pila de operandos
        self.pc = 0                 # Program Counter (contador de programa)
        self.etiquetas = {}         # Mapa de etiquetas a líneas
        self.codigo = []            # Lista de instrucciones
        self.ejecutando = True
        
    def cargar_codigo(self, codigo_p):
        """Carga el código P y construye mapa de etiquetas"""
        self.codigo = []
        
        for i, linea in enumerate(codigo_p):
            linea = linea.strip()
            
            # Ignorar comentarios y líneas vacías
            if linea.startswith(';') or not linea:
                continue
                
            # Detectar etiquetas (lab L0)
            if linea.startswith('lab '):
                etiqueta = linea.split()[1]
                self.etiquetas[etiqueta] = len(self.codigo)
                continue
            
            self.codigo.append(linea)
    
    def ejecutar(self):
        """Ejecuta el código P instrucción por instrucción"""
        self.pc = 0
        self.ejecutando = True
        
        print("\n=== INICIO DE EJECUCIÓN ===\n")
        
        while self.ejecutando and self.pc < len(self.codigo):
            instruccion = self.codigo[self.pc]
            partes = instruccion.split(maxsplit=1)
            opcode = partes[0]
            operando = partes[1] if len(partes) > 1 else None
            
            # Ejecutar instrucción
            self.ejecutar_instruccion(opcode, operando)
            
            self.pc += 1
        
        print("\n=== FIN DE EJECUCIÓN ===\n")
    
    def ejecutar_instruccion(self, opcode, operando):
        """Ejecuta una instrucción individual"""
        
        # Cargar constante
        if opcode == 'ldc':
            valor = self.parsear_valor(operando)
            self.pila.append(valor)
        
        # Cargar variable
        elif opcode == 'lod':
            direccion = int(operando)
            valor = self.memoria[direccion]
            self.pila.append(valor)
        
        # Almacenar en variable
        elif opcode == 'sto':
            direccion = int(operando)
            if self.pila:
                valor = self.pila.pop()
                self.memoria[direccion] = valor
        
        # Operaciones aritméticas
        elif opcode == 'adi':  # Sumar
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(a + b)
        
        elif opcode == 'sbi':  # Restar
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(a - b)
        
        elif opcode == 'mpi':  # Multiplicar
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(a * b)
        
        elif opcode == 'dvi':  # Dividir
            b = self.pila.pop()
            a = self.pila.pop()
            if b != 0:
                self.pila.append(a / b)
            else:
                print("ERROR: División por cero")
                self.pila.append(0)
        
        elif opcode == 'mod':  # Módulo
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(a % b)
        
        # Operaciones relacionales
        elif opcode == 'les':  # Menor que
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if a < b else 0)
        
        elif opcode == 'leq':  # Menor o igual
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if a <= b else 0)
        
        elif opcode == 'grt':  # Mayor que
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if a > b else 0)
        
        elif opcode == 'geq':  # Mayor o igual
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if a >= b else 0)
        
        elif opcode == 'equ':  # Igual
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if a == b else 0)
        
        elif opcode == 'neq':  # Diferente
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if a != b else 0)
        
        # Operadores lógicos
        elif opcode == 'and':
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if (a and b) else 0)
        
        elif opcode == 'or':
            b = self.pila.pop()
            a = self.pila.pop()
            self.pila.append(1 if (a or b) else 0)
        
        # Saltos
        elif opcode == 'ujp':  # Salto incondicional
            self.pc = self.etiquetas[operando] - 1
        
        elif opcode == 'fjp':  # Salto si falso
            condicion = self.pila.pop()
            if not condicion:
                self.pc = self.etiquetas[operando] - 1
        
        # Entrada/Salida
        elif opcode == 'rd':  # Leer
            try:
                valor = float(input())
                # Si es entero, convertir a int
                if valor == int(valor):
                    valor = int(valor)
                self.pila.append(valor)
            except:
                print("ERROR: Entrada inválida")
                self.pila.append(0)
        
        elif opcode == 'wr':  # Escribir
            if self.pila:
                valor = self.pila.pop()
                # Procesar secuencias de escape
                if isinstance(valor, str):
                    valor = valor.strip('"').replace('\\n', '\n').replace('\\t', '\t')
                print(valor, end='')
        
        # Detener
        elif opcode == 'hlt':
            self.ejecutando = False
        
        else:
            print(f"WARNING: Instrucción desconocida: {opcode}")
    
    def parsear_valor(self, operando):
        """Convierte el operando string a su valor apropiado"""
        # Cadena literal
        if operando.startswith('"'):
            return operando.strip('"')
        
        # Número
        try:
            if '.' in operando:
                return float(operando)
            else:
                return int(operando)
        except:
            return operando


# Función principal para ejecutar desde archivo
def ejecutar_codigo_p(codigo_p_lines):
    """Ejecuta una lista de líneas de código P"""
    interprete = InterpreteP()
    interprete.cargar_codigo(codigo_p_lines)
    interprete.ejecutar()


if __name__ == "__main__":
    # Ejemplo de uso
    print("Intérprete de Código P")
    print("Para usar desde el IDE, llama a ejecutar_codigo_p(lista_de_instrucciones)")
