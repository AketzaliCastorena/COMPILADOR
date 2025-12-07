from analisis_lexico import tokenize
from analisis_sintactico import AnalizadorSintactico, ASTNode, Token
from analisis_semantico import AnalizadorSemantico

program = '''
main {
    int i;
    int suma;

    i = 1;
    suma = 0;

    while ( i <= 10 ) {
        if ( i % 2 == 0 ) then {
            suma = suma + i;
        } end
        i = i + 1;
    }

    cout << suma;
}
'''

print('--- Fuente ---')
print(program)

tokens, lex_errors = tokenize(program)
if lex_errors:
    print('\nErrores léxicos:')
    for e in lex_errors:
        print(e)

# Convert tokens to Token objects expected by parser
token_objs = [Token(t[0], t[1], t[2], t[3]) for t in tokens]

parser = AnalizadorSintactico(token_objs)
ast = parser.parse()
if parser.errores:
    print('\nErrores sintácticos:')
    for e in parser.errores:
        print(e)

analizador = AnalizadorSemantico(ast)
tabla, errs, warns, codigo_intermedio, sem_detalle, codigo_p = analizador.analizar()

print('\n--- Código intermedio (Tres direcciones) ---')
for i, ins in enumerate(codigo_intermedio, 1):
    print(f"{i:3d}: {ins}")

print('\n--- Código P (Nemónicos) ---')
for i, ins in enumerate(codigo_p, 1):
    print(f"{i:3d}: {ins}")

print('\nErrores semánticos:', errs)
print('Advertencias:', warns)
