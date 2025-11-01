import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, font
from analisis_lexico import tokenize 
from analisis_sintactico import AnalizadorSintactico, ASTNode, Token
from analisis_semantico import AnalizadorSemantico

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
                "CADENA": "#16a085"# Verde azulado para cadenas
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
        # Eliminar el widget de texto anterior en la pestaña sintáctica
        for widget in self.syntactic_tab.winfo_children():
            widget.destroy()
        self.syntax_errors.winfo_children()[0].delete("1.0", tk.END)

        self.status_label.config(text="Ejecutando análisis sintáctico...")
        self.root.update()

        try:
            # Obtener tokens del análisis léxico
            code = self.text_area.get("1.0", tk.END)
            tokens, _ = tokenize(code)

            # Crear lista de objetos Token
            token_objs = [
                Token(tipo, lexema, linea, columna) for (tipo, lexema, linea, columna) in tokens
            ]

            # Ejecutar análisis sintáctico
            parser = AnalizadorSintactico(token_objs)
            ast = parser.parse()
            
            # Crear frame para el árbol sintáctico
            tree_frame = tk.Frame(self.syntactic_tab)
            tree_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            # Scrollbar vertical
            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Treeview con scrollbar
            tree = ttk.Treeview(
                tree_frame,
                yscrollcommand=vsb.set,
                selectmode="browse"
            )
            tree.pack(expand=True, fill=tk.BOTH)
            
            # Configurar scrollbar
            vsb.config(command=tree.yview)
            
            # Configurar estilo para el árbol
            style = ttk.Style()
            style.configure("Treeview", 
                           font=('Consolas', 10),
                           rowheight=25,
                           background="#ffffff",
                           fieldbackground="#ffffff")
            
            # Configurar solo la columna principal
            tree["columns"] = ("valor", "linea", "columna")
            tree.column("#0", width=250, minwidth=150, stretch=tk.YES)
            tree.column("valor", width=150, anchor=tk.W)
            tree.column("linea", width=80, anchor=tk.CENTER)
            tree.column("columna", width=80, anchor=tk.CENTER)
            
            # Configurar encabezados
            tree.heading("#0", text="Nodo", anchor=tk.W)
            tree.heading("valor", text="Valor", anchor=tk.W)
            tree.heading("linea", text="Línea", anchor=tk.CENTER)
            tree.heading("columna", text="Columna", anchor=tk.CENTER)
            
            # Función recursiva para insertar nodos
            def insertar_nodo(parent, nodo):
                texto = nodo.tipo
                if nodo.valor:
                    texto += f": {nodo.valor}"
                item_id = tree.insert(
                    parent,
                    "end",
                    text=texto,
                    values=(
                        nodo.valor if nodo.valor else "",
                        nodo.linea if nodo.linea is not None else "",
                        nodo.columna if nodo.columna is not None else ""
                    ),
                    open=False
                )
                for hijo in nodo.hijos:
                    insertar_nodo(item_id, hijo)
            
            # Insertar nodo raíz
            insertar_nodo("", ast)
            
            # Botones para expandir/contraer
            btn_frame = tk.Frame(self.syntactic_tab)
            btn_frame.pack(fill=tk.X, padx=5, pady=5)
            
            def expandir_todo():
                for item in tree.get_children():
                    tree.item(item, open=True)
                    expandir_hijos(item)
            
            def expandir_hijos(item):
                for child in tree.get_children(item):
                    tree.item(child, open=True)
                    expandir_hijos(child)
            
            def contraer_todo():
                for item in tree.get_children():
                    tree.item(item, open=False)
            
            ttk.Button(btn_frame, text="Expandir Todo", command=expandir_todo).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Contraer Todo", command=contraer_todo).pack(side=tk.LEFT, padx=5)

            # Mostrar errores
            if parser.errores:
                for error in parser.errores:
                    self.syntax_errors.winfo_children()[0].insert(tk.END, error + "\n", "error")
            else:
                self.syntax_errors.winfo_children()[0].insert(tk.END, "No se encontraron errores sintácticos.\n", "success")

            self.syntax_errors.winfo_children()[0].tag_configure("error", foreground="#e74c3c")
            self.syntax_errors.winfo_children()[0].tag_configure("success", foreground="#27ae60")

            self.tabs.select(1)  # Mostrar tab sintáctico
            self.status_label.config(text="Análisis sintáctico completado")

        except Exception as e:
            self.status_label.config(text=f"Error en análisis sintáctico: {str(e)}")
            self.syntax_errors.winfo_children()[0].insert(tk.END, f"Error: {str(e)}\n", "error")

    def mostrar_arbol_sintactico(self, nodo_raiz):
        ventana = tk.Toplevel(self.root)
        ventana.title("Árbol Sintáctico Abstracto (AST)")
        ventana.geometry("500x600")

        tree = ttk.Treeview(ventana)
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        def insertar_nodo(treeview, parent, nodo):
            texto = nodo.tipo
            if nodo.valor:
                texto += f": {nodo.valor}"
            item_id = treeview.insert(parent, "end", text=texto)
            for hijo in nodo.hijos:
                insertar_nodo(treeview, item_id, hijo)

        insertar_nodo(tree, "", nodo_raiz)

    def semantic_analysis(self):
        self.semantic_tab.winfo_children()[0].delete("1.0", tk.END)
        self.semantic_errors.winfo_children()[0].delete("1.0", tk.END)
        self.hash_table_tab.winfo_children()[0].delete("1.0", tk.END)
        self.intermediate_code_tab.winfo_children()[0].delete("1.0", tk.END)
        
        self.status_label.config(text="Ejecutando análisis semántico...")
        self.root.update()
        
        try:
            # Obtener tokens del análisis léxico
            code = self.text_area.get("1.0", tk.END)
            tokens, _ = tokenize(code)
            
            # Crear lista de objetos Token
            token_objs = [
                Token(tipo, lexema, linea, columna) for (tipo, lexema, linea, columna) in tokens
            ]
            
            # Ejecutar análisis sintáctico
            parser = AnalizadorSintactico(token_objs)
            ast = parser.parse()
            
            # Verificar si hay errores sintácticos
            if parser.errores:
                self.semantic_errors.winfo_children()[0].insert(
                    tk.END, 
                    "⚠️ Advertencia: Existen errores sintácticos. El análisis semántico puede ser incompleto.\n\n",
                    "warning"
                )
            
            # Ejecutar análisis semántico
            analizador = AnalizadorSemantico(ast)
            tabla_simbolos, errores, advertencias, codigo_intermedio, semantico_detalle = analizador.analizar()
            
            # Mostrar tabla semántica detallada con mejor formato
            text_sem = self.semantic_tab.winfo_children()[0]
            header = f"{'NODO':<22}{'TIPO SEMÁNTICO':<18}{'VALOR':<18}{'LÍNEA':<8}{'COL':<6}\n"
            text_sem.insert(tk.END, header, "table_header")
            text_sem.insert(tk.END, "-"*72 + "\n", "separator")
            for info in semantico_detalle:
                nodo = str(info['nodo']) if info['nodo'] is not None else ''
                tipo_sem = str(info['tipo_semantico']) if info['tipo_semantico'] is not None else ''
                valor = str(info['valor']) if info['valor'] is not None else ''
                linea = str(info['linea']) if info['linea'] is not None else ''
                columna = str(info['columna']) if info['columna'] is not None else ''
                fila = f"{nodo:<22}{tipo_sem:<18}{valor:<18}{linea:<8}{columna:<6}\n"
                text_sem.insert(tk.END, fila)
            text_sem.insert(tk.END, "\n" + "="*72 + "\n", "separator")
            
            # Mostrar análisis semántico resumido
            text_sem.insert(tk.END, "✓ ANÁLISIS SEMÁNTICO COMPLETADO\n\n", "title")
            text_sem.insert(tk.END, f"📊 Símbolos encontrados: {len(tabla_simbolos.obtener_simbolos())}\n", "info")
            text_sem.insert(tk.END, f"❌ Errores semánticos: {len(errores)}\n", "error" if errores else "success")
            text_sem.insert(tk.END, f"⚠️  Advertencias: {len(advertencias)}\n", "warning" if advertencias else "success")
            text_sem.insert(tk.END, f"📝 Instrucciones generadas: {len(codigo_intermedio)}\n\n", "info")
            
            if errores or advertencias:
                text_sem.insert(tk.END, "Detalles:\n", "subtitle")
                text_sem.insert(tk.END, "-" * 80 + "\n\n", "separator")
            
            # Configurar estilos
            text_sem.tag_configure("table_header", foreground="#3498db", font=("Consolas", 10, "bold"))
            text_sem.tag_configure("separator", foreground="#95a5a6")
            text_sem.tag_configure("title", foreground="#27ae60", font=("Consolas", 12, "bold"))
            text_sem.tag_configure("subtitle", foreground="#2c3e50", font=("Consolas", 11, "bold"))
            text_sem.tag_configure("info", foreground="#3498db")
            text_sem.tag_configure("success", foreground="#27ae60")
            text_sem.tag_configure("error", foreground="#e74c3c")
            text_sem.tag_configure("warning", foreground="#f39c12")
            
            # Mostrar tabla de símbolos
            text_tabla = self.hash_table_tab.winfo_children()[0]
            text_tabla.insert(tk.END, "=" * 130 + "\n", "header")
            text_tabla.insert(tk.END, "TABLA DE SÍMBOLOS (Hash Table)\n", "header")
            text_tabla.insert(tk.END, "=" * 130 + "\n\n", "header")
            
            simbolos_visuales = tabla_simbolos.obtener_tabla_visual()
            
            if simbolos_visuales:
                # Encabezados
                header = f"{'Identificador':<20} {'Registro':<12} {'Valor':<20} {'Tipo de dato':<15} {'Ámbito':<12} {'Núm. de Línea':<60}\n"
                text_tabla.insert(tk.END, header, "table_header")
                text_tabla.insert(tk.END, "-" * 130 + "\n", "separator")
                
                # Datos
                for simbolo in simbolos_visuales:
                    identificador = str(simbolo['identificador']) if simbolo['identificador'] else ''
                    registro = str(simbolo['registro']) if simbolo['registro'] is not None else ''
                    valor = str(simbolo['valor']) if simbolo['valor'] else ''
                    tipo_dato = str(simbolo['tipo_dato']) if simbolo['tipo_dato'] else ''
                    ambito = str(simbolo['ambito']) if simbolo['ambito'] else ''
                    lineas = str(simbolo['lineas']) if simbolo['lineas'] else ''
                    
                    fila = (
                        f"{identificador:<20} "
                        f"{registro:<12} "
                        f"{valor:<20} "
                        f"{tipo_dato:<15} "
                        f"{ambito:<12} "
                        f"{lineas:<60}\n"
                    )
                    text_tabla.insert(tk.END, fila)
                
                text_tabla.insert(tk.END, "\n" + "=" * 130 + "\n", "separator")
                text_tabla.insert(tk.END, f"Total de símbolos: {len(simbolos_visuales)}\n", "info")
            else:
                text_tabla.insert(tk.END, "No se encontraron símbolos en el programa.\n", "info")
            
            # Configurar estilos para tabla de símbolos
            text_tabla.tag_configure("header", foreground="#2c3e50", font=("Consolas", 11, "bold"))
            text_tabla.tag_configure("table_header", foreground="#3498db", font=("Consolas", 10, "bold"))
            text_tabla.tag_configure("separator", foreground="#95a5a6")
            text_tabla.tag_configure("info", foreground="#27ae60", font=("Consolas", 10, "bold"))
            
            # Mostrar código intermedio
            text_codigo = self.intermediate_code_tab.winfo_children()[0]
            text_codigo.insert(tk.END, "=" * 80 + "\n", "header")
            text_codigo.insert(tk.END, "CÓDIGO INTERMEDIO (Tres Direcciones)\n", "header")
            text_codigo.insert(tk.END, "=" * 80 + "\n\n", "header")
            
            if codigo_intermedio:
                for i, instruccion in enumerate(codigo_intermedio, 1):
                    text_codigo.insert(tk.END, f"{i:3d}:  {instruccion}\n")
                text_codigo.insert(tk.END, "\n" + "=" * 80 + "\n", "separator")
                text_codigo.insert(tk.END, f"Total de instrucciones: {len(codigo_intermedio)}\n", "info")
            else:
                text_codigo.insert(tk.END, "No se generó código intermedio.\n", "info")
            
            # Configurar estilos
            text_codigo.tag_configure("header", foreground="#2c3e50", font=("Consolas", 11, "bold"))
            text_codigo.tag_configure("separator", foreground="#95a5a6")
            text_codigo.tag_configure("info", foreground="#27ae60", font=("Consolas", 10, "bold"))
            
            # Mostrar errores semánticos
            text_errores = self.semantic_errors.winfo_children()[0]
            if errores:
                text_errores.insert(tk.END, "ERRORES SEMÁNTICOS:\n", "header")
                text_errores.insert(tk.END, "=" * 80 + "\n\n", "separator")
                for error in errores:
                    text_errores.insert(tk.END, f"❌ {error}\n\n", "error")
            else:
                text_errores.insert(tk.END, "✓ No se encontraron errores semánticos.\n", "success")
            
            # Mostrar advertencias
            if advertencias:
                text_errores.insert(tk.END, "\n" + "=" * 80 + "\n", "separator")
                text_errores.insert(tk.END, "ADVERTENCIAS:\n", "header")
                text_errores.insert(tk.END, "=" * 80 + "\n\n", "separator")
                for advertencia in advertencias:
                    text_errores.insert(tk.END, f"⚠️  {advertencia}\n\n", "warning")
            
            # Configurar estilos
            text_errores.tag_configure("header", foreground="#2c3e50", font=("Consolas", 11, "bold"))
            text_errores.tag_configure("error", foreground="#e74c3c")
            text_errores.tag_configure("warning", foreground="#f39c12")
            text_errores.tag_configure("success", foreground="#27ae60", font=("Consolas", 11, "bold"))
            text_errores.tag_configure("separator", foreground="#95a5a6")
            
            self.tabs.select(2)  # Mostrar tab semántico
            self.status_label.config(text="Análisis semántico completado")
            
        except Exception as e:
            self.status_label.config(text=f"Error en análisis semántico: {str(e)}")
            text_error = self.semantic_errors.winfo_children()[0]
            text_error.insert(tk.END, f"Error crítico al realizar análisis semántico:\n{str(e)}\n", "error")
            text_error.tag_configure("error", foreground="#e74c3c")

    def execute_code(self):
        self.results.winfo_children()[0].delete("1.0", tk.END)
        self.status_label.config(text="Compilando el código...")
        
        text_result = self.results.winfo_children()[0]
        
        # Ventana de compilación con estilo
        compile_window = tk.Toplevel(self.root)
        compile_window.title("Compilando")
        compile_window.geometry("400x250")
        compile_window.resizable(False, False)
        compile_window.grab_set()  # Hacer modal
        
        # Centrar la ventana
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (250 // 2)
        compile_window.geometry(f"+{x}+{y}")
        
        # Contenido
        frame = tk.Frame(compile_window, bg="white", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(frame, text="Compilación Completa", font=("Arial", 14, "bold"), bg="white")
        title.pack(pady=(0, 15))
        
        status_label = tk.Label(frame, text="Iniciando compilación...", font=("Arial", 11), bg="white")
        status_label.pack(pady=5)
        
        # Barra de progreso
        progress = ttk.Progressbar(frame, mode='indeterminate', length=300)
        progress.pack(pady=15)
        progress.start(10)
        
        # Frame para resultados
        result_frame = tk.Frame(frame, bg="white")
        result_frame.pack(pady=10)
        
        def actualizar_estado(fase, exito):
            simbolo = "✓" if exito else "✗"
            color = "#27ae60" if exito else "#e74c3c"
            label = tk.Label(result_frame, text=f"{simbolo} {fase}", 
                           font=("Arial", 10), bg="white", fg=color)
            label.pack(anchor="w")
            compile_window.update()
        
        try:
            # Fase 1: Análisis Léxico
            status_label.config(text="Fase 1: Análisis Léxico...")
            compile_window.update()
            
            code = self.text_area.get("1.0", tk.END)
            tokens, lex_errors = tokenize(code)
            
            actualizar_estado("Análisis Léxico", len(lex_errors) == 0)
            text_result.insert(tk.END, "═" * 80 + "\n", "header")
            text_result.insert(tk.END, "FASE 1: ANÁLISIS LÉXICO\n", "header")
            text_result.insert(tk.END, "═" * 80 + "\n", "header")
            text_result.insert(tk.END, f"Tokens encontrados: {len(tokens)}\n", "info")
            text_result.insert(tk.END, f"Errores léxicos: {len(lex_errors)}\n\n", 
                             "error" if lex_errors else "success")
            
            if lex_errors:
                for error in lex_errors[:5]:  # Mostrar solo los primeros 5
                    text_result.insert(tk.END, f"  ❌ {error}\n", "error")
                if len(lex_errors) > 5:
                    text_result.insert(tk.END, f"  ... y {len(lex_errors) - 5} errores más\n", "error")
                text_result.insert(tk.END, "\n⚠️ Compilación detenida por errores léxicos.\n", "warning")
                progress.stop()
                return
            
            # Fase 2: Análisis Sintáctico
            status_label.config(text="Fase 2: Análisis Sintáctico...")
            compile_window.update()
            
            token_objs = [Token(tipo, lexema, linea, columna) for (tipo, lexema, linea, columna) in tokens]
            parser = AnalizadorSintactico(token_objs)
            ast = parser.parse()
            
            actualizar_estado("Análisis Sintáctico", len(parser.errores) == 0)
            text_result.insert(tk.END, "═" * 80 + "\n", "header")
            text_result.insert(tk.END, "FASE 2: ANÁLISIS SINTÁCTICO\n", "header")
            text_result.insert(tk.END, "═" * 80 + "\n", "header")
            text_result.insert(tk.END, f"Errores sintácticos: {len(parser.errores)}\n\n", 
                             "error" if parser.errores else "success")
            
            if parser.errores:
                for error in parser.errores[:5]:
                    text_result.insert(tk.END, f"  ❌ {error}\n", "error")
                if len(parser.errores) > 5:
                    text_result.insert(tk.END, f"  ... y {len(parser.errores) - 5} errores más\n", "error")
                text_result.insert(tk.END, "\n⚠️ Compilación detenida por errores sintácticos.\n", "warning")
                progress.stop()
                return
            
            # Fase 3: Análisis Semántico
            status_label.config(text="Fase 3: Análisis Semántico...")
            compile_window.update()
            
            analizador = AnalizadorSemantico(ast)
            tabla_simbolos, sem_errors, advertencias, codigo_intermedio = analizador.analizar()
            
            actualizar_estado("Análisis Semántico", len(sem_errors) == 0)
            text_result.insert(tk.END, "═" * 80 + "\n", "header")
            text_result.insert(tk.END, "FASE 3: ANÁLISIS SEMÁNTICO\n", "header")
            text_result.insert(tk.END, "═" * 80 + "\n", "header")
            text_result.insert(tk.END, f"Símbolos declarados: {len(tabla_simbolos.obtener_simbolos())}\n", "info")
            text_result.insert(tk.END, f"Errores semánticos: {len(sem_errors)}\n", 
                             "error" if sem_errors else "success")
            text_result.insert(tk.END, f"Advertencias: {len(advertencias)}\n\n", 
                             "warning" if advertencias else "success")
            
            if sem_errors:
                for error in sem_errors[:5]:
                    text_result.insert(tk.END, f"  ❌ {error}\n", "error")
                if len(sem_errors) > 5:
                    text_result.insert(tk.END, f"  ... y {len(sem_errors) - 5} errores más\n", "error")
                text_result.insert(tk.END, "\n⚠️ Compilación completada con errores.\n", "warning")
            else:
                text_result.insert(tk.END, "═" * 80 + "\n", "header")
                text_result.insert(tk.END, "✓ COMPILACIÓN EXITOSA\n", "success_big")
                text_result.insert(tk.END, "═" * 80 + "\n", "header")
                text_result.insert(tk.END, f"\n📝 Código intermedio generado: {len(codigo_intermedio)} instrucciones\n", "info")
                text_result.insert(tk.END, f"📊 Variables en tabla de símbolos: {len(tabla_simbolos.obtener_simbolos())}\n", "info")
                
                if advertencias:
                    text_result.insert(tk.END, f"\n⚠️ Se generaron {len(advertencias)} advertencias (ver pestaña de errores semánticos)\n", "warning")
            
            # Configurar estilos
            text_result.tag_configure("header", foreground="#2c3e50", font=("Consolas", 11, "bold"))
            text_result.tag_configure("success_big", foreground="#27ae60", font=("Consolas", 14, "bold"))
            text_result.tag_configure("info", foreground="#3498db")
            text_result.tag_configure("success", foreground="#27ae60")
            text_result.tag_configure("error", foreground="#e74c3c")
            text_result.tag_configure("warning", foreground="#f39c12")
            
            progress.stop()
            status_label.config(text="Compilación completada")
            
            # Botón para cerrar
            btn_close = tk.Button(frame, text="Cerrar", command=compile_window.destroy, 
                    bg=self.colors["accent"], fg="white", relief=tk.FLAT, padx=15, pady=5,
                    font=("Arial", 10))
            btn_close.pack(pady=(10, 0))
            
            self.error_tabs.select(3)  # Mostrar tab de resultados
            self.status_label.config(text="Compilación completada")
            
        except Exception as e:
            progress.stop()
            status_label.config(text="Error en compilación")
            actualizar_estado("Compilación", False)
            text_result.insert(tk.END, f"\n\n❌ Error crítico: {str(e)}\n", "error")
            text_result.tag_configure("error", foreground="#e74c3c", font=("Consolas", 10, "bold"))
            
            btn_close = tk.Button(frame, text="Cerrar", command=compile_window.destroy, 
                    bg="#e74c3c", fg="white", relief=tk.FLAT, padx=15, pady=5)
            btn_close.pack(pady=(10, 0))

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