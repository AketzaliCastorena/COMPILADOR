import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, font
from analisis_lexico import tokenize 

class CompilerIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador IDE")
        self.root.geometry("1200x700")
        self.filename = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuración de colores y estilos
        self.colors = {
            "bg_main": "#f0f2f5",
            "bg_editor": "#ffffff",
            "bg_toolbar": "#2c3e50",
            "fg_toolbar": "#ecf0f1",
            "bg_line_numbers": "#ebedf0",
            "fg_line_numbers": "#7f8c8d",
            "bg_results": "#ffffff",
            "highlight_line": "#f5f5f5",
            "accent": "#3498db",
            "syntax": {
                "NUMERO_ENTERO": "#e74c3c",      # Rojo para números enteros
                "NUMERO_REAL": "#e74c3c",        # Rojo para números reales
                "IDENTIFICADOR": "#0000CD",      # Púrpura para identificadores
                "COMENTARIO_SIMPLE": "#00FF00",  # Verde oscuro para comentarios simples
                "COMENTARIO_MULTILINEA": "#00FF00", # Verde oscuro para comentarios multilinea
                "RESERVADA": "#569CD6",          # Azul para palabras reservadas
                "OPERADOR_ARIT": "#FF69B4",      # Rosa para operadores aritméticos
                "OPERADOR_REL": "#BA55D3",       # Púrpura para operadores relacionales
                "OPERADOR_LOG": "#BA55D3",       # Púrpura para operadores lógicos
                "SIMBOLO": "#ff9800",            # Naranja para símbolos/puntuación
                "CADENA": "#16a085"             # Verde azulado para cadenas
            }
        }

        # Configurar fuente
        self.code_font = font.Font(family="Consolas", size=11)
        
        self.create_toolbar()
        self.create_layout()
        
        # Aplicar tema
        self.root.config(bg=self.colors["bg_main"])
        
        # Configurar estilo para ttk
        self.configure_ttk_style()

    def configure_ttk_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para las pestañas
        style.configure('TNotebook', background=self.colors["bg_main"])
        style.configure('TNotebook.Tab', padding=[10, 5], background=self.colors["bg_toolbar"], 
                        foreground=self.colors["fg_toolbar"])
        style.map('TNotebook.Tab', background=[('selected', self.colors["accent"])],
                  foreground=[('selected', self.colors["fg_toolbar"])])
        
        # Estilo para scrollbars
        style.configure("TScrollbar", background=self.colors["bg_main"], 
                        troughcolor=self.colors["bg_main"],
                        arrowcolor=self.colors["accent"])

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, relief=tk.FLAT, bd=0, bg=self.colors["bg_toolbar"])
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Estilo para los botones
        btn_style = {
            'bg': self.colors["bg_toolbar"], 
            'fg': self.colors["fg_toolbar"],
            'activebackground': self.colors["accent"],
            'activeforeground': self.colors["fg_toolbar"],
            'relief': tk.FLAT,
            'bd': 0,
            'padx': 10,
            'pady': 5,
            'font': ('Arial', 10)
        }
        
        separator_style = {'bg': self.colors["fg_toolbar"], 'height': 20, 'width': 1}

        # Menús
        menu_archivo = tk.Menubutton(toolbar, text="Archivo", **btn_style)
        menu_archivo.menu = tk.Menu(menu_archivo, tearoff=0, bg=self.colors["bg_toolbar"], 
                                 fg=self.colors["fg_toolbar"], activebackground=self.colors["accent"])
        menu_archivo["menu"] = menu_archivo.menu

        menu_archivo.menu.add_command(label="Abrir", command=self.open_file)
        menu_archivo.menu.add_command(label="Guardar", command=self.save_file)
        menu_archivo.menu.add_command(label="Guardar Como", command=self.save_file_as)
        menu_archivo.menu.add_separator()
        menu_archivo.menu.add_command(label="Cerrar", command=self.close_file)

        menu_archivo.pack(side=tk.LEFT, padx=5, pady=6)

        menu_compilador = tk.Menubutton(toolbar, text="Compilador", **btn_style)
        menu_compilador.menu = tk.Menu(menu_compilador, tearoff=0, bg=self.colors["bg_toolbar"], 
                                     fg=self.colors["fg_toolbar"], activebackground=self.colors["accent"])
        menu_compilador["menu"] = menu_compilador.menu

        menu_compilador.menu.add_command(label="Léxico", command=self.lexical_analysis)
        menu_compilador.menu.add_command(label="Sintáctico", command=self.syntax_analysis)
        menu_compilador.menu.add_command(label="Semántico", command=self.semantic_analysis)
        menu_compilador.menu.add_separator()
        menu_compilador.menu.add_command(label="Compilar", command=self.execute_code)

        menu_compilador.pack(side=tk.LEFT, padx=5, pady=6)

        # Separador vertical
        tk.Frame(toolbar, **separator_style).pack(side=tk.LEFT, padx=10, pady=3)

        # Botones con íconos más modernos
        buttons = [
            {"text": "📂", "command": self.open_file, "tooltip": "Abrir archivo"},
            {"text": "💾", "command": self.save_file, "tooltip": "Guardar"},
            {"text": "📄", "command": self.save_file_as, "tooltip": "Guardar como"},
            {"text": "✖️", "command": self.close_file, "tooltip": "Cerrar archivo"}
        ]
        
        btn_style_copy = btn_style.copy()  # Crear una copia del diccionario
        btn_style_copy['font'] = ('Arial', 12)  # Sobreescribir la fuente
        
        for btn in buttons:
            button = tk.Button(toolbar, text=btn["text"], **btn_style_copy)
            button.pack(side=tk.LEFT, padx=3)
            self.create_tooltip(button, btn["tooltip"])
            button.config(command=btn["command"])
        
        # Separador vertical
        tk.Frame(toolbar, **separator_style).pack(side=tk.LEFT, padx=10, pady=3)
        
        # Botones de compilación con estilo
        compile_buttons = [
            {"text": "📑", "command": self.lexical_analysis, "tooltip": "Análisis Léxico", "color": "#3498db"},
            {"text": "📜", "command": self.syntax_analysis, "tooltip": "Análisis Sintáctico", "color": "#2ecc71"},
            {"text": "🔍", "command": self.semantic_analysis, "tooltip": "Análisis Semántico", "color": "#e74c3c"},
            {"text": "🚀", "command": self.execute_code, "tooltip": "Compilar", "color": "#f39c12"}
        ]
        
        btn_style_compiler = btn_style.copy()  # Crear una copia del diccionario 
        btn_style_compiler['font'] = ('Arial', 14)  # Sobreescribir la fuente
        
        for btn in compile_buttons:
            button = tk.Button(toolbar, text=btn["text"], **btn_style_compiler)
            button.pack(side=tk.LEFT, padx=5)
            self.create_tooltip(button, btn["tooltip"])
            button.config(command=btn["command"])
        
        # Indicador de archivo actual
        self.file_indicator = tk.Label(toolbar, text="Sin archivo", bg=self.colors["bg_toolbar"], 
                                     fg=self.colors["fg_toolbar"], font=('Arial', 9))
        self.file_indicator.pack(side=tk.RIGHT, padx=10)

    def create_tooltip(self, widget, text):
        """Crea un tooltip para un widget"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Crea una ventana de nivel superior
            self.tooltip = tk.Toplevel(widget)
            # Evita que aparezca en la barra de tareas
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip, text=text, bg="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def create_layout(self):
        main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, 
                                  sashpad=2, bd=0, bg=self.colors["bg_main"])
        main_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Frame del editor
        editor = tk.Frame(main_frame, bg=self.colors["bg_main"])
        editor.pack(expand=True, fill=tk.BOTH)

        editor_frame = tk.Frame(editor, bg=self.colors["bg_main"])
        editor_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        # Panel de números de línea
        self.line_numbers_frame = tk.Frame(editor_frame, width=40, bg=self.colors["bg_line_numbers"])
        self.line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.line_numbers = tk.Text(self.line_numbers_frame, width=4, padx=4, pady=5, 
                                  bg=self.colors["bg_line_numbers"], 
                                  fg=self.colors["fg_line_numbers"],
                                  font=self.code_font,
                                  state="disabled",
                                  relief=tk.FLAT,
                                  cursor="arrow")
        self.line_numbers.pack(expand=True, fill=tk.Y)

        # Editor de texto con bordes redondeados
        editor_container = tk.Frame(editor_frame, padx=0, pady=0, bg=self.colors["bg_main"], relief=tk.FLAT)
        editor_container.pack(expand=True, side=tk.RIGHT, fill=tk.BOTH)
        
        self.text_area = scrolledtext.ScrolledText(
            editor_container, 
            wrap=tk.NONE, 
            bg=self.colors["bg_editor"], 
            fg="#000000",
            insertbackground="#000000",  # Color del cursor
            font=self.code_font,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            selectbackground=self.colors["accent"],
            selectforeground="white",
            undo=True
        )
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)

        # Barra de estado mejorada
        status_bar = tk.Frame(editor, bg="#ecf0f1", height=25)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.line_col_label = tk.Label(
            status_bar, text="Línea: 1 Columna: 1", 
            bg="#ecf0f1", fg="#2c3e50", 
            font=('Arial', 9), 
            anchor="e"
        )
        self.line_col_label.pack(side=tk.RIGHT, padx=10)
        
        self.status_label = tk.Label(
            status_bar, 
            text="Listo", 
            bg="#ecf0f1", 
            fg="#2c3e50", 
            font=('Arial', 9), 
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Configurar vínculos
        self.text_area.bind("<KeyRelease>", self.update_on_key_release)
        self.text_area.bind("<ButtonRelease-1>", self.update_on_key_release)
        self.text_area.bind("<MouseWheel>", self.update_on_key_release)
        self.text_area.bind("<Configure>", self.update_on_key_release)

        self.text_area.bind("<MouseWheel>", self.sync_scroll)
        self.text_area.bind("<Button-4>", self.sync_scroll)
        self.text_area.bind("<Button-5>", self.sync_scroll)
        self.line_numbers.bind("<MouseWheel>", self.sync_scroll)
        self.line_numbers.bind("<Button-4>", self.sync_scroll)
        self.line_numbers.bind("<Button-5>", self.sync_scroll)

        main_frame.add(editor, stretch="always")

        # Panel de resultados
        results_frame = tk.PanedWindow(main_frame, orient=tk.VERTICAL, sashwidth=4, 
                                     sashpad=2, bd=0, bg=self.colors["bg_main"])

        # Notebook de pestañas mejorado
        self.tabs = ttk.Notebook(results_frame)
        
        # Crear tabs con scroll
        self.lexical_tab = self.create_scrolled_text(self.tabs)
        self.syntactic_tab = self.create_scrolled_text(self.tabs)
        self.semantic_tab = self.create_scrolled_text(self.tabs)
        self.hash_table_tab = self.create_scrolled_text(self.tabs)
        self.intermediate_code_tab = self.create_scrolled_text(self.tabs)

        self.tabs.add(self.lexical_tab, text="Léxico")
        self.tabs.add(self.syntactic_tab, text="Sintáctico")
        self.tabs.add(self.semantic_tab, text="Semántico")
        self.tabs.add(self.hash_table_tab, text="Tabla de Símbolos")
        self.tabs.add(self.intermediate_code_tab, text="Código Intermedio")

        self.tabs.pack(expand=True, fill=tk.BOTH)
        results_frame.add(self.tabs, stretch="always")

        # Frame de errores
        error_frame = tk.Frame(results_frame, bg=self.colors["bg_main"])
        self.error_tabs = ttk.Notebook(error_frame)
        
        # Crear tabs de errores con scroll
        self.lexical_errors = self.create_scrolled_text(self.error_tabs)
        self.syntax_errors = self.create_scrolled_text(self.error_tabs)
        self.semantic_errors = self.create_scrolled_text(self.error_tabs)
        self.results = self.create_scrolled_text(self.error_tabs)

        self.error_tabs.add(self.lexical_errors, text="Errores Léxicos")
        self.error_tabs.add(self.syntax_errors, text="Errores Sintácticos")
        self.error_tabs.add(self.semantic_errors, text="Errores Semánticos")
        self.error_tabs.add(self.results, text="Resultados")

        self.error_tabs.pack(expand=True, fill=tk.BOTH)
        error_frame.pack(expand=True, fill=tk.BOTH)
        results_frame.add(error_frame, stretch="always")

        main_frame.add(results_frame, stretch="always")

    def create_scrolled_text(self, parent):
        """Crea un widget de texto con scroll personalizado"""
        frame = tk.Frame(parent, bg=self.colors["bg_main"])
        
        text_widget = tk.Text(
            frame, 
            wrap=tk.WORD, 
            bg=self.colors["bg_results"],
            fg="#2c3e50",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame

    def open_file(self):
        self.filename = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if self.filename:
            with open(self.filename, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.update_line_numbers()
            self.update_line_col()
            # Actualizar indicador de archivo
            self.file_indicator.config(text=f"Archivo: {self.filename.split('/')[-1]}")
            self.status_label.config(text=f"Archivo abierto: {self.filename}")
            self.resaltar_sintaxis()


    def save_file(self):
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.status_label.config(text=f"Archivo guardado: {self.filename}")
            self.text_area.edit_modified(False)
        else:
            self.save_file_as()

    def save_file_as(self):
        self.filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if self.filename:
            self.save_file()
            # Actualizar indicador de archivo
            self.file_indicator.config(text=f"Archivo: {self.filename.split('/')[-1]}")

    def close_file(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel("Guardar cambios", "¿Deseas guardar los cambios antes de cerrar?")
            if response:
                self.save_file()
            elif response is None:
                return
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.update_line_numbers()
        self.text_area.edit_modified(False)
        self.file_indicator.config(text="Sin archivo")
        self.status_label.config(text="Listo")

    def on_closing(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel("Guardar cambios", "¿Deseas guardar los cambios antes de salir?")
            if response:
                self.save_file()
            elif response is None:
                return
        self.root.destroy()

    def lexical_analysis(self):
        code = self.text_area.get("1.0", tk.END)
        self.lexical_tab.winfo_children()[0].delete("1.0", tk.END)
        self.lexical_errors.winfo_children()[0].delete("1.0", tk.END)
        
        self.status_label.config(text="Realizando análisis léxico...")
        self.root.update()
        
        try:
            tokens, errors = tokenize(code)

            for token in tokens:
                tipo, lexema, linea, columna = token
                text_widget = self.lexical_tab.winfo_children()[0]
                text_widget.insert(tk.END, f"[{tipo}] '{lexema}' (Línea {linea}, Columna {columna})\n")
                
                # Colorear en la pestaña léxica
                last_line = text_widget.index(tk.END + "-1c").split('.')[0]
                text_widget.tag_add(tipo, f"{last_line}.0", f"{last_line}.end")
                text_widget.tag_configure(tipo, foreground=self.get_token_color(tipo))

            text_widget = self.lexical_errors.winfo_children()[0]
            for error in errors:
                text_widget.insert(tk.END, error + "\n", "error")
                
            if not errors:
                text_widget.insert(tk.END, "No se encontraron errores léxicos.\n", "success")
                
            # Configurar estilos para errores
            text_widget.tag_configure("error", foreground="#e74c3c")
            text_widget.tag_configure("success", foreground="#27ae60")
            
            self.tabs.select(0)  # Mostrar tab léxico
            self.status_label.config(text="Análisis léxico completado")

            self.resaltar_sintaxis()  # Esta línea asegura que los tokens se pinten en el editor
            
        except Exception as e:
            self.status_label.config(text=f"Error en análisis léxico: {str(e)}")
            error_text = self.lexical_errors.winfo_children()[0]
            error_text.insert(tk.END, f"Error al realizar análisis léxico: {str(e)}\n", "error")


    def get_token_color(self, token_type):
        """Devuelve el color correspondiente al tipo de token"""
        default_color = "#333333"
        return self.colors["syntax"].get(token_type, default_color)

    def resaltar_sintaxis(self):
        code = self.text_area.get("1.0", tk.END)
        try:
            tokens, _ = tokenize(code)

            # Limpiar etiquetas anteriores
            for tag in self.text_area.tag_names():
                if tag != "sel":
                    self.text_area.tag_remove(tag, "1.0", tk.END)

            # Configurar colores y estilos para los diferentes tipos de tokens
            for tipo, color in self.colors["syntax"].items():
                self.text_area.tag_configure(tipo, foreground=color)
                
                # Aplicar negrita a ciertas categorías
                if tipo in ["RESERVADA"]:
                    self.text_area.tag_configure(
                        tipo,
                        font=(self.code_font.actual("family"), self.code_font.actual("size"), "bold")
                    )
                    
                # Aplicar estilo itálico para comentarios
                if tipo in ["COMENTARIO_SIMPLE", "COMENTARIO_MULTILINEA"]:
                    self.text_area.tag_configure(
                        tipo,
                        font=(self.code_font.actual("family"), self.code_font.actual("size"), "italic")
                    )
                    
                # Estilo para símbolos
                if tipo == "SIMBOLO":
                    self.text_area.tag_configure(
                        tipo,
                        foreground=self.colors["syntax"]["SIMBOLO"]
                    )

            # Aplicar resaltado
            for tipo, lexema, linea, columna in tokens:
                try:
                    linea = int(linea)
                    columna = int(columna)
                except ValueError:
                    continue

                # Manejo de PUNTUACION y mapeo a SIMBOLO (para compatibilidad)
                if tipo == "PUNTUACION":
                    tipo = "SIMBOLO"

                start = f"{linea}.{columna - 1}"
                end = f"{linea}.{columna - 1 + len(lexema)}"

                if tipo in self.colors["syntax"] or tipo == "SIMBOLO":
                    self.text_area.tag_add(tipo, start, end)
        except Exception as e:
            print(f"Error resaltando sintaxis: {e}")

    def highlight_current_line(self):
        """Resalta la línea actual"""
        self.text_area.tag_remove("current_line", "1.0", tk.END)
        cursor_position = self.text_area.index(tk.INSERT)
        line_start = cursor_position.split('.')[0] + ".0"
        line_end = cursor_position.split('.')[0] + ".end+1c"
        self.text_area.tag_add("current_line", line_start, line_end)
        self.text_area.tag_configure("current_line", background=self.colors["highlight_line"])

    def syntax_analysis(self):
        self.syntactic_tab.winfo_children()[0].delete("1.0", tk.END)
        self.syntax_errors.winfo_children()[0].delete("1.0", tk.END)
        
        self.status_label.config(text="Ejecutando análisis sintáctico...")
        self.syntactic_tab.winfo_children()[0].insert(tk.END, "Ejecutando análisis sintáctico...\n")
        self.tabs.select(1)  # Mostrar tab sintáctico

    def semantic_analysis(self):
        self.semantic_tab.winfo_children()[0].delete("1.0", tk.END)
        self.semantic_errors.winfo_children()[0].delete("1.0", tk.END)
        
        self.status_label.config(text="Ejecutando análisis semántico...")
        self.semantic_tab.winfo_children()[0].insert(tk.END, "Ejecutando análisis semántico...\n")
        self.tabs.select(2)  # Mostrar tab semántico

    def execute_code(self):
        self.results.winfo_children()[0].delete("1.0", tk.END)
        self.status_label.config(text="Compilando el código...")
        
        # Ventana de compilación con estilo
        compile_window = tk.Toplevel(self.root)
        compile_window.title("Compilando")
        compile_window.geometry("300x150")
        compile_window.resizable(False, False)
        compile_window.grab_set()  # Hacer modal
        
        # Centrar la ventana
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (150 // 2)
        compile_window.geometry(f"+{x}+{y}")
        
        # Contenido
        frame = tk.Frame(compile_window, bg="white", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Compilando el código...", font=("Arial", 12), bg="white").pack(pady=(0, 15))
        
        # Barra de progreso
        progress = ttk.Progressbar(frame, mode='indeterminate', length=200)
        progress.pack(pady=10)
        progress.start(10)
        
        # Botón para cerrar
        tk.Button(frame, text="Cerrar", command=compile_window.destroy, 
                bg=self.colors["accent"], fg="white", relief=tk.FLAT, padx=10).pack(pady=10)
        
        # Resultado
        self.results.winfo_children()[0].insert(tk.END, "Compilación en proceso...\n")
        self.error_tabs.select(3)  # Mostrar tab de resultados

    def update_line_col(self, event=None):
        cursor_index = self.text_area.index(tk.INSERT)
        line, column = cursor_index.split(".")
        self.line_col_label.config(text=f"Línea: {int(line)} Columna: {int(column) + 1}")

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        line_count = int(self.text_area.index("end-1c").split(".")[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state="disabled")

    def update_on_key_release(self, event=None):
        self.update_line_numbers(event)
        self.update_line_col(event)
        self.sync_scroll(event)
        self.resaltar_sintaxis()
        self.highlight_current_line()

    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerIDE(root)
    root.mainloop()