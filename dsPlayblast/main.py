import os
import logging
from PySide2 import QtWidgets
from dsPlayblast import clientFn
from dsPlayblast import playblastFn
from dsPlayblast import playblastUI
from dsPlayblast import loggingFn

# Start application
app = QtWidgets.QApplication(os.sys.argv)

# Logging
loggingFn.setup_logging()
LOGGER = logging.getLogger(__name__)

# Init interface
mainWindow = playblastUI.PlayblastWindow()
mainWindow.always_on_top = True
mainWindow.show()


# Debug
LOGGER.info(f"Settings: {mainWindow.settings.fileName()}")
LOGGER.info(f"Always on top: {mainWindow.always_on_top}")

os.sys.exit(app.exec_())
