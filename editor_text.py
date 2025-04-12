import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

class CompilerIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador")
        self.root.geometry("1000x600")
        self.filename = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_toolbar()
        self.create_layout()

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, relief=tk.RAISED, bd=2, bg="#d9d9d9")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        menu_archivo = tk.Menubutton(toolbar, text="Archivo")
        menu_archivo.menu = tk.Menu(menu_archivo, tearoff=0)
        menu_archivo["menu"] = menu_archivo.menu

        menu_archivo.menu.add_command(label="Abrir", command=self.open_file)
        menu_archivo.menu.add_command(label="Guardar", command=self.save_file)
        menu_archivo.menu.add_command(label="Guardar Como", command=self.save_file_as)
        menu_archivo.menu.add_separator()
        menu_archivo.menu.add_command(label="Cerrar", command=self.close_file)

        menu_archivo.pack(side=tk.LEFT, padx=4, pady=2)  # Aseguramos que se empaquete correctamente

        menu_compilador = tk.Menubutton(toolbar, text="Compilador")
        menu_compilador.menu = tk.Menu(menu_compilador, tearoff=0)
        menu_compilador["menu"] = menu_compilador.menu
        
        menu_compilador.menu.add_command(label="Lexico", command=self.lexical_analysis)
        menu_compilador.menu.add_command(label="Sintactico", command=self.syntax_analysis)
        menu_compilador.menu.add_command(label="Sematico", command=self.semantic_analysis)
        menu_compilador.menu.add_separator()
        menu_compilador.menu.add_command(label="Compilar", command=self.execute_code)

        menu_compilador.pack(side=tk.LEFT, padx=4, pady=2)
        menu_compilador.config(relief=tk.RAISED, bd=2)

        btn_open = tk.Button(toolbar, text="📂", command=self.open_file)
        btn_open.pack(side=tk.LEFT, padx=4, pady=2)

        btn_save = tk.Button(toolbar, text="💾", command=self.save_file)
        btn_save.pack(side=tk.LEFT, padx=4, pady=2)

        btn_save_as = tk.Button(toolbar, text="💾📝", command=self.save_file_as)
        btn_save_as.pack(side=tk.LEFT, padx=4, pady=2)

        btn_close = tk.Button(toolbar, text="❌", command=self.close_file)
        btn_close.pack(side=tk.LEFT, padx=4, pady=2)

        tk.Label(toolbar, text="|").pack(side=tk.LEFT, padx=2)

        btn_lexical = tk.Button(
            toolbar, text="📑 Léxico", command=self.lexical_analysis
        )
        btn_lexical.pack(side=tk.LEFT, padx=4, pady=2)

        btn_syntax = tk.Button(
            toolbar, text="📜 Sintáctico", command=self.syntax_analysis
        )
        btn_syntax.pack(side=tk.LEFT, padx=4, pady=2)

        btn_semantic = tk.Button(
            toolbar, text="🔍 Semántico", command=self.semantic_analysis
        )
        btn_semantic.pack(side=tk.LEFT, padx=4, pady=2)

        btn_compile = tk.Button(toolbar, text="🚀 Compilar", command=self.execute_code)
        btn_compile.pack(side=tk.LEFT, padx=4, pady=2)

    def create_layout(self):
        main_frame = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        editor = tk.Frame(main_frame)
        editor.pack(expand=True, fill=tk.BOTH)
        
        editor_frame = tk.Frame(editor, bg="#cfd8dc")
        editor_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        
        self.line_numbers_frame = tk.Frame(editor_frame, width=30, bg="#f0f0f0")
        self.line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.line_numbers = tk.Text(
            self.line_numbers_frame,
            width=4,
            padx=4,
            pady=5,
            bg="#f0f0f0",
            state="disabled",
        )
        self.line_numbers.pack(expand=True, fill=tk.Y)

        self.text_area = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.NONE, bg="#ffffff", fg="#000"
        )
        self.text_area.pack(expand=True, side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        self.line_col_label = tk.Label(
            editor, text="Linea: 1 Columna: 1", bg="#cfd8dc", anchor="e"
        )
        self.line_col_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Vincular eventos para actualizar la posición del cursor y la numeración de líneas
        self.text_area.bind("<KeyRelease>", self.update_on_key_release)
        self.text_area.bind("<ButtonRelease-1>", self.update_on_key_release)
        self.text_area.bind("<MouseWheel>", self.update_on_key_release)
        self.text_area.bind("<Configure>", self.update_on_key_release)

        # Sincronizar el desplazamiento del área de texto con la numeración de líneas
        self.text_area.bind("<MouseWheel>", self.sync_scroll)
        self.text_area.bind("<Button-4>", self.sync_scroll)
        self.text_area.bind("<Button-5>", self.sync_scroll)
        self.line_numbers.bind("<MouseWheel>", self.sync_scroll)
        self.line_numbers.bind("<Button-4>", self.sync_scroll)
        self.line_numbers.bind("<Button-5>", self.sync_scroll)

        main_frame.add(editor, stretch="always")

        results_frame = tk.PanedWindow(
            main_frame, orient=tk.VERTICAL, sashwidth=5, sashrelief=tk.RAISED
        )

        self.tabs = ttk.Notebook(results_frame)
        self.lexical_tab = tk.Text(self.tabs, wrap=tk.WORD, bg="#ffffff")
        self.syntactic_tab = tk.Text(self.tabs, wrap=tk.WORD, bg="#ffffff")
        self.semantic_tab = tk.Text(self.tabs, wrap=tk.WORD, bg="#ffffff")
        self.hash_table_tab = tk.Text(self.tabs, wrap=tk.WORD, bg="#ffffff")
        self.intermediate_code_tab = tk.Text(self.tabs, wrap=tk.WORD, bg="#ffffff")

        self.tabs.add(self.lexical_tab, text="Léxico")
        self.tabs.add(self.syntactic_tab, text="Sintáctico")
        self.tabs.add(self.semantic_tab, text="Semántico")
        self.tabs.add(self.hash_table_tab, text="Tabla de Símbolos")
        self.tabs.add(self.intermediate_code_tab, text="Código Intermedio")

        self.tabs.pack(expand=True, fill=tk.BOTH)
        results_frame.add(self.tabs, stretch="always")

        error_frame = tk.Frame(results_frame, bg="#eceff1")
        self.error_tabs = ttk.Notebook(error_frame)
        self.lexical_errors = tk.Text(self.error_tabs, wrap=tk.WORD, bg="#ffffff")
        self.syntax_errors = tk.Text(self.error_tabs, wrap=tk.WORD, bg="#ffffff")
        self.semantic_errors = tk.Text(self.error_tabs, wrap=tk.WORD, bg="#ffffff")
        self.results = tk.Text(self.error_tabs, wrap=tk.WORD, bg="#ffffff")

        self.error_tabs.add(self.lexical_errors, text="Errores Léxicos")
        self.error_tabs.add(self.syntax_errors, text="Errores Sintácticos")
        self.error_tabs.add(self.semantic_errors, text="Errores Semánticos")
        self.error_tabs.add(self.results, text="Resultados")

        self.error_tabs.pack(expand=True, fill=tk.BOTH)
        error_frame.pack(expand=True, fill=tk.BOTH)
        results_frame.add(error_frame, stretch="always")

        main_frame.add(results_frame, stretch="always")

    def open_file(self):
        self.filename = filedialog.askopenfilename()
        if self.filename:
            with open(self.filename, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.update_line_numbers()
            self.update_line_col()

    def save_file(self):
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if self.filename:
            self.save_file()

    def close_file(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Guardar cambios", "¿Deseas guardar los cambios antes de cerrar?"
            )
            if response:
                self.save_file()
            elif response is None:
                return

        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.update_line_numbers()
        self.text_area.edit_modified(False)

    def on_closing(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Guardar cambios", "¿Deseas guardar los cambios antes de salir?"
            )
            if response:
                self.save_file()
            elif response is None:
                return

        self.root.destroy()

    def lexical_analysis(self):
        self.lexical_tab.insert(tk.END, "Ejecutando análisis léxico...\n")

    def syntax_analysis(self):
        self.syntactic_tab.insert(tk.END, "Ejecutando análisis sintáctico...\n")

    def semantic_analysis(self):
        self.semantic_tab.insert(tk.END, "Ejecutando análisis semántico...\n")

    def execute_code(self):
        messagebox.showinfo("Compilación", "Compilando el código...")

    def update_line_col(self, event=None):
        # Obtener la posición actual del cursor
        cursor_index = self.text_area.index(tk.INSERT)
        line, column = cursor_index.split(".")

        # Reiniciar la columna en cada fila
        line = int(line)  # Convertir a entero para asegurarnos de que sea un número
        column = int(column)  # Convertir a entero para asegurarnos de que sea un número
        self.line_col_label.config(text=f"Linea: {line} Columna: {column}")

    def update_line_numbers(self, event=None):
        # Actualizar la numeración de líneas
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)

        # Obtener el número total de líneas
        line_count = int(self.text_area.index("end-1c").split(".")[0])

        # Generar la numeración de líneas
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))

        # Insertar la numeración en el widget de líneas
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state="disabled")

    def update_on_key_release(self, event=None):
        # Actualizar la posición del cursor y la numeración de líneas
        self.update_line_numbers(event)
        self.update_line_col(event)
        self.sync_scroll(event)

    def sync_scroll(self, event=None):
        # Sincronizar el desplazamiento del área de texto con la numeración de líneas
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerIDE(root)
    root.mainloop() 