from os import path, system
from PySide6.QtWidgets import *
from sys import argv, exit
from typing import Optional

# pyinstaller --windowed --onefile main.py

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.variables: dict[str, Optional[str]] = {
            "binary": "ffmpeg",
            "images_directory": None,
            "extension": "jpg",
            "framerate": "30",
            "w": "1920",
            "h": "1080",
            "x": None,
            "y": None,
            "colour": "yuvj420p",
            "encoder": "libx264",
            "bitrate": None,
            "output_directory": path.expanduser("~/Downloads"),
        }

        # Window Options
        self.setWindowTitle("Timelapse")

        # Layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        widgets = [
            [
                FileWidget(self),
                SelectWidget(self, "extension", ["jpg", "tiff"], "Extension")
            ],
            InputWidget(self, ["w", "h"], "Size"),
            InputWidget(self, ["x", "y"], "Position"),
            [
                SelectWidget(self, "framerate", ["30", "60", "120"], "Framerate"),
                SelectWidget(self, "colour", ["yuvj420p"], "Colour"),
            ],
            [
                SelectWidget(self, "encoder", ["libx264"], "Encoder"),
                InputWidget(self, ["bitrate"], "Bitrate"),
            ],
        ]

        self.create_layout(widgets, layout)

        create_button = QPushButton("Create")
        create_button.clicked.connect(self.create_timelapse)
        layout.addWidget(create_button)

    @property
    def cmd(self):
        print(self.variables)
        if not all(self.variables.values()):
            return None
        
        return "{binary} -pattern_type glob -i '{images_directory}/*.{extension}' -framerate {framerate} -filter:v crop=x={x}:y={y}:w={w}:h={h} -pix_fmt {colour} -c:v {encoder} -b:v {bitrate}M {output_directory}/timelapse.mp4 ".format(**self.variables)

    def create_layout(self, widgets: list[QWidget], parent_layout: QVBoxLayout | QHBoxLayout):
        for widget in widgets:
            if isinstance(widget, list):
                widget_layout = QHBoxLayout()
                self.create_layout(widget, widget_layout)
                parent_layout.addLayout(widget_layout)
            else:
                parent_layout.addWidget(widget)

    def set_variable(self, name: str, value: str):
        self.variables[name] = value

    def create_timelapse(self):
        if not self.cmd:
            QMessageBox.critical(self, "Error", "Not all variables have been set.")
            return  
            
        system(self.cmd)


class FileWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.parent = parent

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.file_button = QPushButton("Select Directory")
        self.file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.file_button)

    def open_file_dialog(self):
        directory = QFileDialog.getExistingDirectory(
            self.parent,
            "Select Directory",
        )
        if directory:
            self.parent.set_variable("images_directory", directory)


class InputWidget(QWidget):
    def __init__(self, parent: QWidget, keys: list[str], label: str, separator = "x"):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        label = QLabel(label, self)
        layout.addWidget(label)

        for i, key in enumerate(keys):
            input = QLineEdit(self)
            input.setText(parent.variables[key])
            input.editingFinished.connect(lambda key=key, input=input: parent.set_variable(key, input.text()))
            layout.addWidget(input)

            if i < len(keys) - 1:
                separator = QLabel(separator, self)
                layout.addWidget(separator)


class SelectWidget(QWidget):
    def __init__(self, parent: QWidget, key: str, items: list[str], label: Optional[str] = None):
        super().__init__(parent)

        layout = QFormLayout(self)
        self.setLayout(layout)

        default_item_index = items.index(parent.variables[key])

        widget = QComboBox()
        widget.addItems(items)
        widget.setCurrentIndex(default_item_index)
        widget.currentTextChanged.connect(lambda: parent.set_variable(key, widget.currentText()))
        layout.addRow(label or key, widget)

if __name__ == "__main__":
    app = QApplication(argv)

    window = Window()
    window.show()

    exit(app.exec())