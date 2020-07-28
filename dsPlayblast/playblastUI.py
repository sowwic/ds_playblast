import logging
import os
import time
import webbrowser
from PySide2 import QtWidgets
from PySide2 import QtCore
from dsPlayblast import __version__
from dsPlayblast import __author__
from dsPlayblast import ffmpegFn
from dsPlayblast import widgets
from dsPlayblast import clientFn

LOGGER = logging.getLogger(__name__)


class PlayblastWindow(QtWidgets.QMainWindow):

    resolutions = [[320, 480, "320x480"],
                   [640, 480, "640x480"],
                   [960, 540, "HD_540"],
                   [1280, 720, "HD_720"],
                   [1920, 1080, "HD_1080"]]

    def __init__(self):
        super().__init__()
        # General settings
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.setWindowTitle("dsPlayblast")
        self.setMinimumSize(300, 400)

        # Load base settings
        self.settings = QtCore.QSettings("dsPlayblast", "main")
        self.always_on_top = self.settings.value("always_on_top", defaultValue=0)
        self.maya_client = clientFn.MayaClient(port=self.settings.value("maya_port", defaultValue=7221))
        self.resize(self.settings.value("window_width", defaultValue=400), self.settings.value("window_height", defaultValue=560))

        # Build UI
        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.validate_paths()

    @property
    def always_on_top(self) -> int:
        return self._always_on_top

    @always_on_top.setter
    def always_on_top(self, state):
        self._always_on_top = int(state)
        if state:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    # Events
    def closeEvent(self, event):
        super().closeEvent(event)
        self.save_settings()
        try:
            self.maya_client.disconnect()
        except AttributeError:
            pass

    # Settings
    def save_settings(self):
        # Window
        self.settings.setValue("window_width", self.width())
        self.settings.setValue("window_height", self.height())
        # Client
        self.settings.setValue("maya_port", self.maya_client.port)
        # Action
        self.settings.setValue("always_on_top", self.always_on_top)

        # Ffmpeg
        self.settings.setValue("ffmpeg_path", self.ffmpeg_path.path_line_edit.text())

        # Time range
        self.settings.setValue("time_range_mode", int(self.time_range.timeslider_radio.isChecked()))
        self.settings.setValue("time_range_start_time", int(self.time_range.start_time.value()))
        self.settings.setValue("time_range_end_time", int(self.time_range.end_time.value()))

        # Image
        self.settings.setValue("image_size_index", self.image_size.currentIndex())
        self.settings.setValue("image_quality", self.image_quality.spin_box.value())
        self.settings.setValue("image_scale", self.image_scale.spin_box.value())
        self.settings.setValue("image_frame_padding", self.image_frame_padding.spin_box.value())
        # Output
        self.settings.setValue("output_path", self.output_path.get_path())
        self.settings.setValue("output_viewer_checkbox_checked", int(self.output_viewer_checkbox.isChecked()))
        self.settings.setValue("output_ornaments_checkbox_checked", int(self.output_ornaments_checkbox.isChecked()))
        self.settings.setValue("output_removetemp_checkbox_checked", int(self.output_removetemp_checkbox.isChecked()))
        self.settings.setValue("output_clearcache_checkbox_checked", int(self.output_clearcache_checkbox.isChecked()))
        self.settings.setValue("output_offscreen_checkbox_checked", int(self.output_offscreen_checkbox.isChecked()))

    # Build components
    def create_actions(self):
        # Create actions
        self.set_maya_port_action = QtWidgets.QAction("Set Maya port", self)
        self.always_on_top_action = QtWidgets.QAction("Window always on top", self)
        self.always_on_top_action.setCheckable(1)
        self.always_on_top_action.setChecked(self.settings.value("always_on_top", 0))
        self.ffmpeg_help_action = QtWidgets.QAction("FFmpeg download", self)
        self.ffmpeg_help_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogHelpButton))
        self.about_help_action = QtWidgets.QAction("About", self)

        # Create menus
        self.options_menu = self.menuBar().addMenu("&Options")
        self.options_menu.addAction(self.set_maya_port_action)
        self.options_menu.addAction(self.always_on_top_action)

        self.help_menu = self.menuBar().addMenu("Help")
        self.help_menu.addAction(self.ffmpeg_help_action)
        self.help_menu.addAction(self.about_help_action)

    def create_widgets(self):
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.scroll_widget = widgets.ScrollWidget()

        # ffmpeg widgets
        self.ffmpeg_grp = QtWidgets.QGroupBox("Converter")
        self.ffmpeg_path = widgets.BrowsePath(lable_text="FFmpeg exe:",
                                              mode="openFile",
                                              default_path=self.settings.value("ffmpeg_path", defaultValue=" "),
                                              file_dialog_title="Select FFmpeg executable",
                                              filters="ffmpeg.exe",
                                              button_text="...")
        # Time range
        self.time_range_grp = QtWidgets.QGroupBox("Time")
        self.time_range = widgets.TimeRange(mode=self.settings.value("time_range_mode", defaultValue=0),
                                            start_time=self.settings.value("time_range_start_time", defaultValue=0),
                                            end_time=self.settings.value("time_range_end_time", defaultValue=120))

        # Image settings
        self.image_grp = QtWidgets.QGroupBox("Image")
        self.image_size = QtWidgets.QComboBox()
        self.image_size.addItems([res[2] for res in PlayblastWindow.resolutions])
        self.image_size.setCurrentIndex(self.settings.value("image_size_index", defaultValue=0))
        self.image_scale = widgets.FieldSliderGroup(data_type="float",
                                                    label_text="Scale:",
                                                    min_value=0.1,
                                                    max_value=1.0,
                                                    default_value=self.settings.value("image_scale", defaultValue=1.0),
                                                    step=0.1,
                                                    slider_multiplier=100.0)
        self.image_frame_padding = widgets.FieldSliderGroup(data_type="int",
                                                            label_text="Frame padding:",
                                                            min_value=0,
                                                            max_value=4,
                                                            step=1.0,
                                                            default_value=self.settings.value("image_frame_padding", defaultValue=4),
                                                            slider_multiplier=1.0)
        self.image_quality = widgets.FieldSliderGroup(data_type="int",
                                                      label_text="Quality:",
                                                      min_value=0,
                                                      max_value=100,
                                                      step=1.0,
                                                      default_value=self.settings.value("image_quality", defaultValue=75),
                                                      slider_multiplier=1.0)

        # Output prefs
        self.output_grp = QtWidgets.QGroupBox("Output")
        self.output_path = widgets.BrowsePath(lable_text="Output file:",
                                              button_text="...",
                                              mode="saveFile",
                                              default_path=self.settings.value("output_path", defaultValue=""),
                                              file_dialog_title="Save playblast as",
                                              filters="*.mp4")
        self.output_viewer_checkbox = QtWidgets.QCheckBox("Open viewer")
        self.output_ornaments_checkbox = QtWidgets.QCheckBox("Show ornaments")
        self.output_removetemp_checkbox = QtWidgets.QCheckBox("Removed temporary files")
        self.output_offscreen_checkbox = QtWidgets.QCheckBox("Render offscreen")
        self.output_clearcache_checkbox = QtWidgets.QCheckBox("Clear cache")
        self.output_viewer_checkbox.setChecked(self.settings.value("output_viewer_checkbox_checked", defaultValue=1))
        self.output_ornaments_checkbox.setChecked(self.settings.value("output_ornaments_checkbox_checked", defaultValue=1))
        self.output_removetemp_checkbox.setChecked(self.settings.value("output_removetemp_checkbox_checked", defaultValue=1))
        self.output_clearcache_checkbox.setChecked(self.settings.value("output_clearcache_checkbox_checked", defaultValue=1))
        self.output_offscreen_checkbox.setChecked(self.settings.value("output_offscreen_checkbox_checked", defaultValue=0))

        # Buttons
        self.playblast_btn = QtWidgets.QPushButton("Playblast")
        self.playblast_btn.setMinimumHeight(25)

        # Status bar
        # self.statusBar = QtWidgets.QStatusBar()
        self.statusBar = widgets.StatusLogger(level="INFO", timeout=4000)
        self.statusBar.setFormatter(LOGGER.parent.handlers[0].formatter)
        self.statusBar.widget.setMaximumHeight(17)
        LOGGER.addHandler(self.statusBar)
        self.progressBar = widgets.dsProgressBar()
        self.progressBar.setMaximumWidth(90)
        self.progressBar.hide()
        self.statusBar.widget.addPermanentWidget(self.progressBar)

    def create_layouts(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.scroll_widget)
        self.scroll_widget.contentLayout.addWidget(self.ffmpeg_grp)
        self.scroll_widget.contentLayout.addWidget(self.time_range_grp)
        self.scroll_widget.contentLayout.addWidget(self.image_grp)
        self.scroll_widget.contentLayout.addWidget(self.output_grp)
        self.main_layout.addWidget(self.time_range)
        self.main_layout.addWidget(self.playblast_btn)
        self.main_layout.addWidget(self.statusBar.widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.ffmpeg_layout = QtWidgets.QVBoxLayout()
        self.ffmpeg_layout.addWidget(self.ffmpeg_path)
        self.ffmpeg_grp.setLayout(self.ffmpeg_layout)

        self.time_range_layout = QtWidgets.QVBoxLayout()
        self.time_range_layout.addWidget(self.time_range)
        self.time_range_grp.setLayout(self.time_range_layout)

        self.image_layout = QtWidgets.QVBoxLayout()
        self.image_layout.addWidget(self.image_size)
        self.image_layout.addWidget(self.image_quality)
        self.image_layout.addWidget(self.image_scale)
        self.image_layout.addWidget(self.image_frame_padding)
        self.image_grp.setLayout(self.image_layout)

        self.output_layout = QtWidgets.QVBoxLayout()
        self.output_layout.addWidget(self.output_path)
        self.output_layout.addWidget(self.output_viewer_checkbox)
        self.output_layout.addWidget(self.output_ornaments_checkbox)
        self.output_layout.addWidget(self.output_removetemp_checkbox)
        self.output_layout.addWidget(self.output_clearcache_checkbox)
        self.output_layout.addWidget(self.output_offscreen_checkbox)
        self.output_grp.setLayout(self.output_layout)

    def create_connections(self):
        # Actions
        self.always_on_top_action.toggled.connect(self.toggle_always_on_top)
        self.set_maya_port_action.triggered.connect(self.set_maya_port)
        self.ffmpeg_help_action.triggered.connect(self.open_ffmpeg_web)
        self.about_help_action.triggered.connect(self.diplay_about_info)

        # Inputs
        self.ffmpeg_path.path_line_edit.textChanged.connect(self.validate_paths)
        self.output_path.path_line_edit.textChanged.connect(self.validate_paths)

        # Buttons
        self.playblast_btn.clicked.connect(self.playblast)

        # Status bar
        self.progressBar.valueChanged.connect(self.logProgress)

    @ QtCore.Slot()
    def toggle_always_on_top(self) -> None:
        self.always_on_top = not self.always_on_top

    @ QtCore.Slot()
    def open_ffmpeg_web(self):
        webbrowser.open(url="https://ffmpeg.org/", new=2, autoraise=True)

    @QtCore.Slot()
    def diplay_about_info(self):
        info_dialog = QtWidgets.QMessageBox(self)
        info_dialog.setWindowTitle("About")
        info_dialog.setText(f"Author: {__author__}\nVersion: {__version__}")
        info_dialog.exec_()

    @ QtCore.Slot()
    def connect_to_maya(self) -> None:
        LOGGER.info(f"TODO: Connecting to maya port {self.maya_client.port}")

    @ QtCore.Slot()
    def set_maya_port(self) -> None:
        value, result = QtWidgets.QInputDialog.getInt(self, "Maya port",
                                                      "Current port:",
                                                      value=self.maya_client.port,
                                                      minValue=1025,
                                                      maxValue=65535)
        if not result:
            return

        self.maya_client.port = value
        LOGGER.info(f"Maya port set to {value}")

    @ QtCore.Slot()
    def validate_paths(self):
        if len(self.output_path.path_line_edit.text().split("/")) < 2 or not self.ffmpeg_path.path_line_edit.text().endswith("ffmpeg.exe"):
            self.playblast_btn.setEnabled(False)
        else:
            self.playblast_btn.setEnabled(True)

    @ QtCore.Slot()
    def logProgress(self, value):
        if value == 0:
            LOGGER.info("Initializing")
        elif value == 1:
            LOGGER.info("Connecting to Maya...")
        elif value == 2:
            LOGGER.info("Connected.")
        elif value == 3:
            LOGGER.info("Playblasting as avi...")
        elif value == 4:
            LOGGER.info("Converting to mp4")
        elif value == 5:
            LOGGER.info("Done.")

    @ QtCore.Slot()
    def update_progress_bar(self):
        self.progressBar.setValue(self.progressBar.value() + 1)
        QtCore.QCoreApplication.processEvents()
        time.sleep(0.2)

    @ QtCore.Slot()
    def playblast(self) -> None:
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(5)
        self.progressBar.setValue(0)
        self.progressBar.show()

        # Playblast
        self.update_progress_bar()
        if not self.maya_client.connect():
            LOGGER.error("Failed to connect to Maya")
            self.progressBar.hide()
            return

        self.update_progress_bar()
        avi_result_path = self.output_path.get_path().replace(".mp4", ".avi")
        self.update_progress_bar()
        self.maya_client.send(self.playblast_command())
        self.update_progress_bar()

        # Conversion
        converter = ffmpegFn.Converter(self.ffmpeg_path.get_path(),
                                       input_path=avi_result_path,
                                       output_path=self.output_path.get_path())
        errorStatus = converter.convert_avi_to_mp4()
        if errorStatus:
            QtCore.QCoreApplication.processEvents()
            LOGGER.error(f"Failed to convert {avi_result_path}")
            self.progressBar.hide()
            return

        self.update_progress_bar()
        os.remove(avi_result_path)
        self.progressBar.hide()
        if self.output_viewer_checkbox.isChecked():
            os.startfile(self.output_path.get_path())

    def playblast_command(self) -> str:
        avi_result_path = self.output_path.get_path().replace(".mp4", ".avi")
        ornaments = self.output_ornaments_checkbox.isChecked()
        quality = self.image_quality.spin_box.value()
        offscreen = self.output_offscreen_checkbox.isChecked()
        frame_padding = self.image_frame_padding.spin_box.value()
        clear_cache = self.output_clearcache_checkbox.isChecked()
        width, height = self.resolutions[self.image_size.currentIndex()][:2]
        percent = self.image_scale.slider.value()
        if self.time_range.startend_radio.isChecked():
            start_time = self.time_range.start_time.value()
            end_time = self.time_range.end_time.value()
        else:
            start_time, end_time = self.get_maya_playback_time()

        cmd = f"maya.cmds.playblast(f='{avi_result_path}', cc={clear_cache}, orn={ornaments}, qlt={quality}, os={offscreen}, fp={frame_padding}, h={height}, w={width}, p={percent}, st={start_time}, et={end_time}, v=0, fmt='avi', fo=1)"
        return cmd

    def get_maya_playback_time(self):
        start_time = self.maya_client.send("maya.cmds.playbackOptions(min=1, q=1)")
        end_time = self.maya_client.send("maya.cmds.playbackOptions(max=1, q=1)")

        start_time = float(start_time.strip("\n"))
        end_time = float(end_time.strip("\n"))
        return start_time, end_time
