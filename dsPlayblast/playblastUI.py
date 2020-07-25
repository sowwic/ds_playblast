import logging
from PySide2 import QtWidgets
from PySide2 import QtCore
from dsPlayblast import util

LOGGER = logging.getLogger(__name__)


class PlayblastWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Settings
        self.settings = QtCore.QSettings("dsPlayblast", "main")
        self.always_on_top = self.settings.value("always_on_top", defaultValue=False)

        # Build UI
        self.createActions()
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    @property
    def always_on_top(self) -> bool:
        return self._always_on_top

    @always_on_top.setter
    def always_on_top(self, state):
        if isinstance(state, str):
            state = util.str_to_bool(state)
        self._always_on_top = state
        if state:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    @QtCore.Slot()
    def toggle_always_on_top(self) -> None:
        self.always_on_top = not self.always_on_top
        self.testButton.setText(str(self.always_on_top))

    # Events
    def closeEvent(self, event):
        super().closeEvent(event)
        self.save_settings()

    # Settings
    def save_settings(self):
        self.settings.setValue("always_on_top", self.always_on_top)

    # Build components
    def createActions(self):
        pass

    def createWidgets(self):
        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)

        self.testButton = QtWidgets.QPushButton(str(self.always_on_top))

    def createLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.testButton)

    def createConnections(self):
        self.testButton.clicked.connect(self.toggle_always_on_top)
