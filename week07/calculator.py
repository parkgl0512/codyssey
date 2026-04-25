"""
Calculator Application
iOS-style dark theme calculator with full arithmetic operations.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QVBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics


# ---------------------------------------------------------------------------
# Core Calculator Logic
# ---------------------------------------------------------------------------

class Calculator:
    """Handles all calculator state and arithmetic operations."""

    MAX_DIGITS = 15

    def __init__(self):
        self._current = '0'
        self._stored = None
        self._operator = None
        self._awaiting_operand = False
        self._result_shown = False

    # ---- Properties --------------------------------------------------------

    @property
    def display(self):
        return self._current

    # ---- Digit / Decimal input --------------------------------------------

    def input_digit(self, digit: str) -> str:
        """Append a digit to the current number."""
        if self._awaiting_operand or self._result_shown:
            self._current = digit
            self._awaiting_operand = False
            self._result_shown = False
        else:
            if self._current == '0' and digit != '.':
                self._current = digit
            elif len(self._current.replace('-', '').replace('.', '')) < self.MAX_DIGITS:
                self._current += digit
        return self._current

    def input_decimal(self) -> str:
        """Insert a decimal point if not already present."""
        if self._awaiting_operand or self._result_shown:
            self._current = '0.'
            self._awaiting_operand = False
            self._result_shown = False
        elif '.' not in self._current:
            self._current += '.'
        return self._current

    # ---- Operators ---------------------------------------------------------

    def set_operator(self, op: str) -> str:
        """Store current value and set pending operator."""
        current_val = self._parse(self._current)
        if self._operator and not self._awaiting_operand:
            result = self._compute(self._stored, current_val, self._operator)
            if result is None:
                return self._current
            self._stored = result
            self._current = self._format(result)
        else:
            self._stored = current_val
        self._operator = op
        self._awaiting_operand = True
        return self._current

    def add(self) -> str:
        return self.set_operator('+')

    def subtract(self) -> str:
        return self.set_operator('-')

    def multiply(self) -> str:
        return self.set_operator('\u00d7')

    def divide(self) -> str:
        return self.set_operator('\u00f7')

    # ---- Result ------------------------------------------------------------

    def equal(self) -> str:
        """Compute and display result."""
        if self._operator is None:
            return self._current
        current_val = self._parse(self._current)
        result = self._compute(self._stored, current_val, self._operator)
        if result is None:
            self._current = 'Error'
        else:
            self._current = self._format(result)
        self._operator = None
        self._stored = None
        self._awaiting_operand = False
        self._result_shown = True
        return self._current

    # ---- Utility operations ------------------------------------------------

    def reset(self) -> str:
        """AC - clear everything."""
        self._current = '0'
        self._stored = None
        self._operator = None
        self._awaiting_operand = False
        self._result_shown = False
        return self._current

    def negative_positive(self) -> str:
        """Toggle sign of the current number."""
        val = self._parse(self._current)
        if val == 0:
            return self._current
        result = val * -1
        self._current = self._format(result)
        return self._current

    def percent(self) -> str:
        """Divide current number by 100."""
        val = self._parse(self._current)
        result = val / 100
        self._current = self._format(result)
        return self._current

    # ---- Internal helpers --------------------------------------------------

    @staticmethod
    def _parse(text: str) -> float:
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _compute(self, a, b, op):
        """Return result or None on math error."""
        try:
            if op == '+':
                result = a + b
            elif op == '-':
                result = a - b
            elif op == '\u00d7':
                result = a * b
            elif op == '\u00f7':
                if b == 0:
                    return None  # Division by zero
                result = a / b
            else:
                return None
            # Overflow guard
            if abs(result) > 1e15:
                return None
            return result
        except OverflowError:
            return None

    @staticmethod
    def _format(value: float) -> str:
        """Format a float for display.

        Bonus requirements:
        - Rounds to at most 6 decimal places.
        - Strips unnecessary trailing zeros and decimal points.
        - Displays as an integer when the result is whole.
        """
        if abs(value) > 1e15:
            return 'Error'
        # Step 1: round to 6 decimal places
        rounded = round(value, 6)
        # Step 2: if the rounded result is a whole number, show without decimals
        if rounded == int(rounded):
            return str(int(rounded))
        # Step 3: format to 6 decimal places then strip trailing zeros
        text = f'{rounded:.6f}'.rstrip('0')
        return text


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

BTN_RADIUS = 38

# Color palette
CLR_BG = '#1c1c1e'
CLR_FUNC_BG = '#a5a5a5'
CLR_FUNC_FG = '#1c1c1e'
CLR_FUNC_PRESS = '#d4d4d2'
CLR_OP_BG = '#ff9f0a'
CLR_OP_FG = '#ffffff'
CLR_OP_PRESS = '#ffd085'
CLR_OP_ACTIVE_BG = '#ffffff'
CLR_OP_ACTIVE_FG = '#ff9f0a'
CLR_DIGIT_BG = '#333333'
CLR_DIGIT_FG = '#ffffff'
CLR_DIGIT_PRESS = '#636366'


def _btn_style(bg, fg, align='center', pl=0):
    """Generate a stylesheet string for a button."""
    return (
        f'QPushButton {{'
        f'  border: none;'
        f'  border-radius: {BTN_RADIUS}px;'
        f'  font-size: 26px;'
        f'  color: {fg};'
        f'  background-color: {bg};'
        f'  text-align: {align};'
        f'  padding-left: {pl}px;'
        f'}}'
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

class CalculatorWindow(QMainWindow):
    """Main window - iOS-style dark calculator."""

    def __init__(self):
        super().__init__()
        self._calc = Calculator()
        self._active_op_btn = None  # (QPushButton, normal_stylesheet)
        self._last_display_text = '0'
        self._build_ui()

    def showEvent(self, event):
        """Re-apply font size once the widget has a real pixel width."""
        super().showEvent(event)
        self._update_font_size(self._last_display_text)

    # ---- Build UI ----------------------------------------------------------

    def _build_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(414, 736)
        self.setStyleSheet(f'background-color: {CLR_BG};')

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Display -------------------------------------------------------
        self._display = QLabel('0')
        self._display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self._display.setContentsMargins(20, 0, 20, 16)
        self._display.setStyleSheet('color: #ffffff; background: transparent;')
        self._update_font_size('0')
        root.addWidget(self._display, stretch=1)

        # ---- Buttons -------------------------------------------------------
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(12, 8, 12, 20)
        grid.setSpacing(10)

        # (label, row, col, colspan, category)
        # category: 'func' | 'op' | 'num' | 'num_wide'
        layout = [
            ('AC',        0, 0, 1, 'func'),
            ('+/-',       0, 1, 1, 'func'),
            ('%',         0, 2, 1, 'func'),
            ('\u00f7',    0, 3, 1, 'op'),
            ('7',         1, 0, 1, 'num'),
            ('8',         1, 1, 1, 'num'),
            ('9',         1, 2, 1, 'num'),
            ('\u00d7',    1, 3, 1, 'op'),
            ('4',         2, 0, 1, 'num'),
            ('5',         2, 1, 1, 'num'),
            ('6',         2, 2, 1, 'num'),
            ('-',         2, 3, 1, 'op'),
            ('1',         3, 0, 1, 'num'),
            ('2',         3, 1, 1, 'num'),
            ('3',         3, 2, 1, 'num'),
            ('+',         3, 3, 1, 'op'),
            ('0',         4, 0, 2, 'num_wide'),
            ('.',         4, 2, 1, 'num'),
            ('=',         4, 3, 1, 'op'),
        ]

        self._op_buttons = {}

        for label, row, col, span, cat in layout:
            btn = QPushButton(label)
            btn.setMinimumHeight(78)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            if cat == 'func':
                ns = _btn_style(CLR_FUNC_BG, CLR_FUNC_FG)
                ps = _btn_style(CLR_FUNC_PRESS, CLR_FUNC_FG)
                btn.setStyleSheet(ns)
                btn.pressed.connect(lambda b=btn, p=ps: b.setStyleSheet(p))
                btn.released.connect(lambda b=btn, n=ns: b.setStyleSheet(n))
                if label == 'AC':
                    btn.clicked.connect(self._on_reset)
                elif label == '+/-':
                    btn.clicked.connect(self._on_neg_pos)
                else:
                    btn.clicked.connect(self._on_percent)

            elif cat == 'op':
                ns = _btn_style(CLR_OP_BG, CLR_OP_FG)
                ps = _btn_style(CLR_OP_PRESS, CLR_OP_FG)
                act = _btn_style(CLR_OP_ACTIVE_BG, CLR_OP_ACTIVE_FG)
                btn.setStyleSheet(ns)
                btn.pressed.connect(lambda b=btn, p=ps: b.setStyleSheet(p))
                btn.released.connect(lambda b=btn, n=ns: b.setStyleSheet(n))
                self._op_buttons[label] = (btn, ns, act)
                if label == '=':
                    btn.clicked.connect(self._on_equal)
                else:
                    btn.clicked.connect(lambda checked, op=label: self._on_operator(op))

            elif cat == 'num_wide':
                ns = _btn_style(CLR_DIGIT_BG, CLR_DIGIT_FG, align='left', pl=30)
                ps = _btn_style(CLR_DIGIT_PRESS, CLR_DIGIT_FG, align='left', pl=30)
                btn.setStyleSheet(ns)
                btn.pressed.connect(lambda b=btn, p=ps: b.setStyleSheet(p))
                btn.released.connect(lambda b=btn, n=ns: b.setStyleSheet(n))
                btn.clicked.connect(lambda: self._on_digit('0'))

            else:  # 'num'
                ns = _btn_style(CLR_DIGIT_BG, CLR_DIGIT_FG)
                ps = _btn_style(CLR_DIGIT_PRESS, CLR_DIGIT_FG)
                btn.setStyleSheet(ns)
                btn.pressed.connect(lambda b=btn, p=ps: b.setStyleSheet(p))
                btn.released.connect(lambda b=btn, n=ns: b.setStyleSheet(n))
                if label == '.':
                    btn.clicked.connect(self._on_decimal)
                else:
                    btn.clicked.connect(lambda checked, d=label: self._on_digit(d))

            grid.addWidget(btn, row, col, 1, span)

        for i in range(5):
            grid.setRowStretch(i, 1)
        for i in range(4):
            grid.setColumnStretch(i, 1)

        root.addWidget(grid_widget)

    # ---- Event handlers ----------------------------------------------------

    def _on_digit(self, d: str):
        self._clear_active_op()
        self._set_display(self._calc.input_digit(d))

    def _on_decimal(self):
        self._clear_active_op()
        self._set_display(self._calc.input_decimal())

    def _on_operator(self, op: str):
        self._clear_active_op()
        self._set_display(self._calc.set_operator(op))
        if op in self._op_buttons:
            btn, ns, act = self._op_buttons[op]
            btn.setStyleSheet(act)
            self._active_op_btn = (btn, ns)

    def _on_equal(self):
        self._clear_active_op()
        self._set_display(self._calc.equal())

    def _on_reset(self):
        self._clear_active_op()
        self._set_display(self._calc.reset())

    def _on_neg_pos(self):
        self._set_display(self._calc.negative_positive())

    def _on_percent(self):
        self._set_display(self._calc.percent())

    # ---- Display helpers ---------------------------------------------------

    def _set_display(self, value: str):
        formatted = self._add_commas(value)
        self._last_display_text = formatted  # keep latest for showEvent
        self._display.setText(formatted)
        self._update_font_size(formatted)

    @staticmethod
    def _add_commas(value: str) -> str:
        """Add thousands separators to the integer part."""
        if value == 'Error':
            return value
        if '.' in value:
            int_part, dec_part = value.split('.', 1)
        else:
            int_part, dec_part = value, None
        negative = int_part.startswith('-')
        digits = int_part.lstrip('-')
        try:
            int(digits)
            grouped = f'{int(digits):,}'
        except ValueError:
            grouped = digits
        result = ('-' if negative else '') + grouped
        if dec_part is not None:
            result += '.' + dec_part
        return result

    def _update_font_size(self, text: str):
        """Bonus: shrink font until the full text fits on one line.

        Measures actual rendered pixel width via QFontMetrics so that
        every digit, decimal point, and comma is always fully visible.
        """
        # Use the label's own width when available; fall back to window width.
        label_width = self._display.width()
        if label_width <= 0:
            label_width = self.width()
        # Subtract left + right content margins set on the label (20 + 20 = 40)
        available_width = label_width - 40
        if available_width <= 0:
            available_width = 334  # 414 window - 40 padding - 40 safety margin

        # Step down from 80 pt until the text fits within the available width.
        for size in range(80, 19, -2):
            font = QFont('SF Pro Display', size, QFont.Light)
            font.setStyleHint(QFont.SansSerif)
            fm = QFontMetrics(font)
            if fm.horizontalAdvance(text) <= available_width:
                self._display.setFont(font)
                return
        # Fallback: minimum readable size
        font = QFont('SF Pro Display', 20, QFont.Light)
        font.setStyleHint(QFont.SansSerif)
        self._display.setFont(font)

    def _clear_active_op(self):
        if self._active_op_btn:
            btn, ns = self._active_op_btn
            btn.setStyleSheet(ns)
            self._active_op_btn = None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Calculator')
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()