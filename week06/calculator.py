import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # 연산 상태 변수
        self.current_value = ''
        self.operator = ''
        self.operand = ''

    def init_ui(self):
        self.setWindowTitle('Calculator')

        grid = QGridLayout()
        self.setLayout(grid)

        # 디스플레이
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60)
        grid.addWidget(self.display, 0, 0, 1, 4)

        # 버튼 구성 (아이폰 계산기 스타일)
        buttons = [
            ('AC', 1, 0), ('±', 1, 1), ('%', 1, 2), ('÷', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('×', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('0', 5, 0), ('.', 5, 2), ('=', 5, 3)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFixedHeight(50)

            if text == '0':
                grid.addWidget(button, row, col, 1, 2)
            else:
                grid.addWidget(button, row, col)

            button.clicked.connect(self.on_click)

    def on_click(self):
        sender = self.sender()
        text = sender.text()

        if text.isdigit() or text == '.':
            self.current_value += text
            self.display.setText(self.current_value)

        elif text in ['+', '-', '×', '÷']:
            self.operator = text
            self.operand = self.current_value
            self.current_value = ''

        elif text == '=':
            self.calculate()

        elif text == 'AC':
            self.current_value = ''
            self.operator = ''
            self.operand = ''
            self.display.clear()

        elif text == '±':
            if self.current_value:
                if self.current_value.startswith('-'):
                    self.current_value = self.current_value[1:]
                else:
                    self.current_value = '-' + self.current_value
                self.display.setText(self.current_value)

        elif text == '%':
            if self.current_value:
                self.current_value = str(float(self.current_value) / 100)
                self.display.setText(self.current_value)

    def calculate(self):
        if not self.operator or not self.operand or not self.current_value:
            return

        try:
            a = float(self.operand)
            b = float(self.current_value)

            if self.operator == '+':
                result = a + b
            elif self.operator == '-':
                result = a - b
            elif self.operator == '×':
                result = a * b
            elif self.operator == '÷':
                if b == 0:
                    self.display.setText('Error')
                    return
                result = a / b

            self.display.setText(str(result))
            self.current_value = str(result)
            self.operator = ''
            self.operand = ''

        except Exception:
            self.display.setText('Error')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())