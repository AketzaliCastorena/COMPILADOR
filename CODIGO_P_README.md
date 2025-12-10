# Generador de Código P - Compilador

## Descripción
El compilador ahora genera **Código P** (código de máquina con nemónicos) a partir del código fuente. El código P utiliza una arquitectura basada en pila con los siguientes nemónicos:

## Tabla de Nemónicos

### Carga y Almacenamiento
- `lda` - Load address
- `ldc <valor>` - Load constant (carga constante en la pila)
- `lod <dir>` - Load (carga valor de dirección de memoria)
- `sto <dir>` - Store (almacena valor de la pila en memoria)

### Operaciones Aritméticas y Lógicas
- `adi` - Add integer (suma)
- `sbi` - Subtract integer (resta)
- `mpi` - Multiply integer (multiplicación)
- `dvi` - Divide integer (división)
- `mod` - Módulo
- `pot` - Potencia
- `and` - AND lógico
- `or` - OR lógico

### Operaciones de Comparación
- `les` - Less than (<)
- `grt` - Greater than (>)
- `equ` - Equal (==)
- `les eq` - Less or equal (<=)
- `grt eq` - Greater or equal (>=)

### Control de Flujo
- `ujp <label>` - Unconditional jump (salto incondicional)
- `fjp <label>` - False jump (salto si falso)
- `lab <label>` - Label (etiqueta)
- `hlt` - Halt (detener programa)

### Entrada/Salida
- `rd` - Read (leer entrada)
- `wr` - Write (escribir salida)

## Ejemplo de Uso

### Código Fuente:
```c
main {
    int x, y, z;
    x = 10;
    y = 5;
    z = x + y;
    cout << z;
}
```

### Código P Generado:
```
  1:  ldc 10
  2:  sto 0
  3:  ldc 5
  4:  sto 1
  5:  lod 0
  6:  lod 1
  7:  adi
  8:  sto 2
  9:  lod 2
 10:  wr
 11:  hlt
```

## Arquitectura

El código P funciona con una **arquitectura basada en pila**:

1. **Memoria**: Las variables se asignan a direcciones de memoria secuenciales (0, 1, 2, ...)
2. **Pila**: Las operaciones cargan valores a la pila, operan sobre ellos y almacenan resultados
3. **Flujo**: Uso de etiquetas y saltos para implementar estructuras de control (if, while, etc.)

## Operaciones Típicas

### Asignación Simple
```
x = 10;
```
Genera:
```
ldc 10    ; Cargar constante 10
sto 0     ; Almacenar en x (dirección 0)
```

### Operación Aritmética
```
z = x + y;
```
Genera:
```
lod 0     ; Cargar x
lod 1     ; Cargar y
adi       ; Sumar (resultado en pila)
sto 2     ; Almacenar en z
```

### Estructura If-Else
```c
if (x > y) {
    z = x;
} else {
    z = y;
}
```
Genera:
```
lod 0     ; Cargar x
lod 1     ; Cargar y
grt       ; Comparar >
fjp L1    ; Saltar a L1 si falso
lod 0     ; Cargar x
sto 2     ; Almacenar en z
ujp L2    ; Saltar a L2
lab L1    ; Etiqueta else
lod 1     ; Cargar y
sto 2     ; Almacenar en z
lab L2    ; Etiqueta fin
```

### Entrada/Salida
```c
cin >> x;
cout << x;
```
Genera:
```
rd        ; Leer entrada
sto 0     ; Almacenar en x
lod 0     ; Cargar x
wr        ; Escribir salida
```

## Visualización en el IDE

El código P se muestra en la pestaña **"Código intermedio"** del IDE, en dos secciones:

1. **Código de Tres Direcciones**: Representación intermedia legible
2. **Código P**: Nemónicos de máquina listos para ejecutar

## Notas Técnicas

- Las direcciones de memoria se asignan automáticamente de forma secuencial
- Los temporales (t0, t1, t2...) también reciben direcciones de memoria
- Las etiquetas (L0, L1, L2...) se usan para saltos y estructuras de control
- El operador `!=` se implementa como `equ` seguido de negación
- Cada programa termina con `hlt`

## Compatibilidad

El generador de código P es compatible con todos los tipos de datos y estructuras del lenguaje:
- ✅ Variables (int, float, bool)
- ✅ Operaciones aritméticas (+, -, *, /, %)
- ✅ Operaciones relacionales (<, >, <=, >=, ==, !=)
- ✅ Operaciones lógicas (&&, ||, !)
- ✅ Estructuras de control (if-else, while, do-while)
- ✅ Entrada/Salida (cin, cout)
- ✅ Operadores unarios (++, --)
