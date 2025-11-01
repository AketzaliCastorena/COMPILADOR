# Compilador - Fases 1, 2 y 3 Completas

Este es un compilador educativo completo que implementa las tres primeras fases de compilación:
- **Fase 1**: Análisis Léxico
- **Fase 2**: Análisis Sintáctico
- **Fase 3**: Análisis Semántico y Generación de Código Intermedio

## 📋 Características Implementadas

### Análisis Léxico
- Reconocimiento de tokens:
  - Palabras reservadas: `if`, `else`, `while`, `do`, `int`, `float`, `bool`, `main`, `cin`, `cout`, etc.
  - Identificadores
  - Números enteros y reales
  - Operadores aritméticos: `+`, `-`, `*`, `/`, `%`, `^`, `++`, `--`
  - Operadores relacionales: `<`, `>`, `<=`, `>=`, `==`, `!=`
  - Operadores lógicos: `&&`, `||`, `!`
  - Símbolos: `(`, `)`, `{`, `}`, `;`, `,`, etc.
  - Comentarios simples (`//`) y multilinea (`/* */`)
- Detección de errores léxicos
- Resaltado de sintaxis en tiempo real

### Análisis Sintáctico
- Parser descendente recursivo
- Construcción de Árbol Sintáctico Abstracto (AST)
- Gramática soportada:
  - Declaraciones de variables
  - Asignaciones
  - Estructuras de control: `if-else`, `while`, `do-while`
  - Expresiones aritméticas con precedencia de operadores
  - Operadores lógicos y relacionales
  - Entrada/Salida: `cin`, `cout`
- Visualización del AST en formato de árbol
- Recuperación de errores sintácticos

### Análisis Semántico (Nueva Fase)
- **Tabla de Símbolos**:
  - Implementada con función hash
  - Almacena información de variables (nombre, tipo, línea, columna)
  - Detecta declaraciones duplicadas
  - Visualización completa de la tabla
  
- **Verificación de Tipos**:
  - Comprobación de compatibilidad en asignaciones
  - Validación de operaciones según tipos
  - Conversión implícita de `int` a `float`
  
- **Análisis de Variables**:
  - Detección de variables no declaradas
  - Advertencias por variables no inicializadas
  - Advertencias por variables declaradas pero no usadas
  
- **Generación de Código Intermedio**:
  - Código de tres direcciones
  - Generación de temporales
  - Generación de etiquetas para estructuras de control
  - Instrucciones para todas las operaciones

## 🚀 Uso del Compilador

### Ejecutar el IDE
```bash
python compiler_ide.py
```

### Operaciones Disponibles

1. **Análisis Léxico** (📑): Tokeniza el código fuente
2. **Análisis Sintáctico** (📜): Construye el AST
3. **Análisis Semántico** (🔍): Verifica tipos y genera tabla de símbolos
4. **Compilar** (🚀): Ejecuta todas las fases en secuencia

### Pestañas de Resultados

- **Léxico**: Lista de tokens reconocidos
- **Sintáctico**: Árbol sintáctico abstracto
- **Semántico**: Resumen del análisis semántico
- **Tabla de Símbolos**: Tabla hash con variables declaradas
- **Código Intermedio**: Código de tres direcciones generado

### Pestañas de Errores

- **Errores Léxicos**: Caracteres inválidos, tokens mal formados
- **Errores Sintácticos**: Errores de estructura del programa
- **Errores Semánticos**: Errores de tipos, variables no declaradas, etc.
- **Resultados**: Resumen de la compilación completa

## 📝 Sintaxis del Lenguaje

### Estructura Básica
```
main {
    // Declaraciones y sentencias
}
```

### Declaración de Variables
```
int x, y, z;
float resultado;
bool bandera;
```

### Asignaciones
```
x = 10;
y = x + 5;
resultado = 3.14 * x;
```

### Operadores
```
// Aritméticos
x = a + b - c * d / e % f;
x++;
y--;
potencia = base ^ exponente;

// Relacionales
if (x > 10) { }
if (y <= 5) { }
if (a == b) { }
if (x != y) { }

// Lógicos
if (x > 0 && y < 10) { }
if (flag || !otro) { }
```

### Estructuras de Control
```
// If-Else
if (condicion) {
    // sentencias
} else {
    // sentencias
}

// While
while (condicion) {
    // sentencias
}

// Do-While
do {
    // sentencias
} while (condicion);
```

### Entrada/Salida
```
cin >> variable;
cout << "Texto" << variable;
```

## 🔍 Ejemplo Completo

Vea el archivo `ejemplo_prueba.txt` para un ejemplo completo que demuestra todas las características del compilador.

## 📊 Tabla de Símbolos

La tabla de símbolos muestra:
- **Índice**: Posición en la tabla hash
- **Nombre**: Identificador de la variable
- **Tipo**: int, float, o bool
- **Línea/Columna**: Ubicación de la declaración
- **Inicializado**: Si la variable ha sido asignada
- **Usado**: Si la variable se usa en el programa

## 💻 Código Intermedio

El código de tres direcciones incluye:
- Declaraciones: `DECLARE variable tipo`
- Asignaciones: `variable = expresion`
- Operaciones: `temp = op1 operador op2`
- Saltos condicionales: `if condicion goto etiqueta`
- Saltos incondicionales: `goto etiqueta`
- Etiquetas: `L0:`, `L1:`, etc.
- E/S: `READ variable`, `WRITE variable`

## 🎨 Características de la IDE

- Editor con numeración de líneas
- Resaltado de sintaxis en tiempo real
- Indicador de posición del cursor
- Múltiples pestañas para resultados
- Árbol expandible para el AST
- Colores diferenciados para:
  - Palabras reservadas (azul)
  - Números (rojo)
  - Identificadores (azul oscuro)
  - Comentarios (verde)
  - Operadores (rosa/púrpura)
  - Cadenas (verde azulado)

## 🔧 Archivos del Proyecto

- `compiler_ide.py`: IDE principal con interfaz gráfica
- `analisis_lexico.py`: Analizador léxico (tokenizador)
- `analisis_sintactico.py`: Parser y construcción del AST
- `analisis_semantico.py`: Análisis semántico y código intermedio
- `editor_text.py`: Editor de texto antiguo (no usado)
- `colores_synta.py`: Resaltado de sintaxis (PyQt5, no usado)
- `ejemplo_prueba.txt`: Programa de ejemplo

## ⚠️ Notas Importantes

1. El compilador requiere Python 3.x con tkinter
2. La fase 3 (análisis semántico) está completamente implementada
3. Se detectan errores en todas las fases de compilación
4. Las advertencias no detienen la compilación
5. La tabla de símbolos usa una función hash simple

## 🎯 Reglas Semánticas Implementadas

1. **Variables deben ser declaradas antes de usarse**
2. **No se permiten declaraciones duplicadas**
3. **Tipos deben ser compatibles en asignaciones**
4. **Operadores deben aplicarse a tipos válidos**
5. **Condiciones deben ser de tipo bool** (advertencia)
6. **Variables deben inicializarse antes de usarse** (advertencia)
7. **Variables declaradas deben usarse** (advertencia)

## 📚 Referencia

Implementado según las especificaciones del documento:
**"Fase 3: Análisis Semántico - 2025"**

---

**Desarrollado como proyecto educativo de Compiladores**
