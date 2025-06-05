from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont # type: ignore
import re

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Definición de colores según el documento
        color_num = QColor("#FFD700")       # Color 1 - Números
        color_id = QColor("#00CED1")        # Color 2 - Identificadores
        color_comment = QColor("#6A9955")   # Color 3 - Comentarios
        color_keyword = QColor("#569CD6")   # Color 4 - Palabras reservadas
        color_op_arit = QColor("#FF69B4")   # Color 5 - Operadores aritméticos
        color_op_rel_log = QColor("#BA55D3")# Color 6 - Operadores relacionales y lógicos

        # Reglas para números
        number_format = QTextCharFormat()
        number_format.setForeground(color_num)
        self.highlighting_rules.append((re.compile(r"[+-]?\d+\.\d+|[+-]?\d+"), number_format))

        # Reglas para identificadores (no comenzando con dígito)
        id_format = QTextCharFormat()
        id_format.setForeground(color_id)
        self.highlighting_rules.append((re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"), id_format))

        # Reglas para comentarios
        comment_format = QTextCharFormat()
        comment_format.setForeground(color_comment)
        self.highlighting_rules.append((re.compile(r"//.*"), comment_format))
        self.highlighting_rules.append((re.compile(r"/\*.*?\*/", re.DOTALL), comment_format))

        # Palabras reservadas
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(color_keyword)
        keywords = r"\b(if|else|end|do|while|switch|case|int|float|main|cin|cout)\b"
        self.highlighting_rules.append((re.compile(keywords), keyword_format))

        # Operadores aritméticos
        arit_format = QTextCharFormat()
        arit_format.setForeground(color_op_arit)
        self.highlighting_rules.append((re.compile(r"\+\+|--|\+|-|\*|/|%|\^"), arit_format))

        # Operadores relacionales y lógicos
        rel_log_format = QTextCharFormat()
        rel_log_format.setForeground(color_op_rel_log)
        self.highlighting_rules.append((re.compile(r"<=|>=|==|!=|<|>|&&|\|\||!"), rel_log_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)