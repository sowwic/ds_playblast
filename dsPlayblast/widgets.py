import logging
from PySide2 import QtWidgets
from PySide2 import QtCore


LOGGER = logging.getLogger(__name__)


class FieldSliderGroup(QtWidgets.QWidget):
    def __init__(self, parent=None,
                 data_type="int",
                 min_value=0.0,
                 max_value=1.0,
                 default_value=1.0,
                 step=1.0,
                 slider_multiplier=1.0,
                 label_text: str = ""):
        super().__init__(parent)
        # Properties
        self.data_type = data_type
        self.setMinimumSize(100, 40)

        # Build components
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # Set values
        self.slide_multiplier = slider_multiplier
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value
        self.step = step

        if isinstance(default_value, str):
            if data_type == "float":
                default_value = float(default_value)
            elif data_type == "int":
                default_value = int(default_value)
        self.spin_box.setValue(default_value)

    @property
    def label_text(self):
        return self._label_text

    @label_text.setter
    def label_text(self, text):
        self._label_text = str(text)
        self.label.setText(str(text))

    @property
    def min_value(self):
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        self._min_value = value
        self.spin_box.setMinimum(value)
        self.slider.setMinimum(value * self.slide_multiplier)

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        self._max_value = value
        self.spin_box.setMaximum(value)
        self.slider.setMaximum(value * self.slide_multiplier)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value
        self.spin_box.setSingleStep(value)

    def create_widgets(self):
        if self.data_type == "float":
            self.spin_box = QtWidgets.QDoubleSpinBox()
        elif self.data_type == "int":
            self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setMinimumWidth(40)
        self.label = QtWidgets.QLabel()
        self.spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.addWidget(self.label, 0, 0)
        self.main_layout.addWidget(self.spin_box, 0, 1)
        self.main_layout.addWidget(self.slider, 0, 2)
        self.main_layout.setColumnMinimumWidth(0, 90)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.spin_box.valueChanged.connect(self.set_slider_value)
        self.slider.valueChanged.connect(self.set_field_value)

    @QtCore.Slot()
    def set_field_value(self, value):
        self.spin_box.setValue(value / self.slide_multiplier)

    @QtCore.Slot()
    def set_slider_value(self, value):
        self.slider.setValue(value * self.slide_multiplier)


class BrowsePath(QtWidgets.QWidget):
    def __init__(self,
                 parent=None,
                 mode="dir",
                 lable_text="",
                 default_path="",
                 button_text="",
                 button_icon="",
                 file_dialog_title="Select",
                 filters=""):

        super().__init__(parent)
        self.label_text = lable_text
        self.defaut_path = default_path
        self.button_icon = button_icon
        self.button_text = button_text
        self.file_dialog_title = file_dialog_title
        self.filters = filters
        self.mode = mode

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.label = QtWidgets.QLabel(self.label_text)
        self.path_line_edit = QtWidgets.QLineEdit(self.defaut_path)
        self.browse_button = QtWidgets.QPushButton(text=self.button_text)
        if self.button_icon:
            self.browse_button.setIcon(self.button_icon)

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.path_line_edit)
        self.main_layout.addWidget(self.browse_button)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_connections(self):
        if self.mode == "dir":
            self.browse_button.clicked.connect(self.get_existing_dir)
        elif self.mode == "openFile":
            self.browse_button.clicked.connect(self.get_existing_file)
        elif self.mode == "saveFile":
            self.browse_button.clicked.connect(self.get_new_file)
        else:
            LOGGER.error("Invalid browse widget mode. Should be one of: 'dir', 'openFile', 'saveFile'", exc_info=1)

    @QtCore.Slot()
    def get_existing_dir(self):
        result = QtWidgets.QFileDialog.getExistingDirectory(self, self.file_dialog_title, self.path_line_edit.text())
        if not result:
            return
        self.path_line_edit.setText(result)

    @QtCore.Slot()
    def get_existing_file(self):
        result = QtWidgets.QFileDialog.getOpenFileName(self, self.file_dialog_title, self.path_line_edit.text(), self.filters)[0]
        if not result:
            return
        self.path_line_edit.setText(result)

    @QtCore.Slot()
    def get_new_file(self):
        result = QtWidgets.QFileDialog.getSaveFileName(self, self.file_dialog_title, self.path_line_edit.text(), self.filters)[0]
        if not result:
            return
        self.path_line_edit.setText(result)

    def get_path(self) -> str:
        return self.path_line_edit.text()


class ScrollWidget(QtWidgets.QWidget):
    def __init__(self, border=0, **kwargs):
        super(ScrollWidget, self).__init__(**kwargs)

        self.content = QtWidgets.QWidget(self)
        self.scrollArea = QtWidgets.QScrollArea()

        self.scrollArea.setWidget(self.content)
        self.scrollArea.setWidgetResizable(1)

        self.contentLayout = QtWidgets.QVBoxLayout(self.content)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.scrollArea)
        self.layout().setContentsMargins(0, 0, 0, 0)

        if not border:
            self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)

    def resizeEvent(self, e):
        self.scrollArea.resizeEvent(e)


class StatusLogger(logging.Handler):
    def __init__(self, level="DEBUG", parent=None, timeout=3000):
        super().__init__(level)
        self.widget = QtWidgets.QStatusBar(parent)
        self.timeout = timeout

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.widget.showMessage(msg, self.timeout)


class dsProgressBar(QtWidgets.QProgressBar):

    visibilityChanged = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=None)

    def showEvent(self, event):
        self.visibilityChanged.emit(True)

    def hideEvent(self, event):
        self.visibilityChanged.emit(False)
