import logging
from PySide2 import QtWidgets
from PySide2 import QtCore
from dsPlayblast import util
from dsPlayblast import ffmpegFn
from dsPlayblast import widgets

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

        # Settings
        self.settings = QtCore.QSettings("dsPlayblast", "main")
        self.always_on_top = self.settings.value("always_on_top", defaultValue=False)
        self.resize(self.settings.value("window_width", defaultValue=400), self.settings.value("window_height", defaultValue=560))

        # Build UI
        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

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

    # Events
    def closeEvent(self, event):
        super().closeEvent(event)
        self.save_settings()

    # Settings
    def save_settings(self):
        self.settings.setValue("always_on_top", self.always_on_top)
        self.settings.setValue("ffmpeg_path", self.ffmpeg_path.path_line_edit.text())

    # Build components
    def create_actions(self):
        pass

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

        # Image settings
        self.image_grp = QtWidgets.QGroupBox("Image")
        self.image_mode = QtWidgets.QComboBox()
        self.image_mode.addItems([res[2] for res in PlayblastWindow.resolutions])
        self.image_mode.setCurrentIndex(self.settings.value("image_mode_index", defaultValue=0))
        self.image_scale = widgets.FieldSliderGroup(data_type="float",
                                                    label_text="Scale:",
                                                    min_value=0.1,
                                                    max_value=1.0,
                                                    default_value=1.0,
                                                    step=0.1,
                                                    slider_multiplier=100.0)
        self.image_frame_padding = widgets.FieldSliderGroup(data_type="int",
                                                            label_text="Frame padding:",
                                                            min_value=0,
                                                            max_value=4,
                                                            step=1.0,
                                                            default_value=4.0,
                                                            slider_multiplier=1.0)
        self.image_quality = widgets.FieldSliderGroup(data_type="int",
                                                      label_text="Quality:",
                                                      min_value=0,
                                                      max_value=100,
                                                      step=1.0,
                                                      default_value=75,
                                                      slider_multiplier=1.0)

        # Output prefs
        self.output_grp = QtWidgets.QGroupBox("Output")
        self.output_path = widgets.BrowsePath(lable_text="Output file:",
                                              button_text="...",
                                              mode="saveFile",
                                              default_path=self.settings.value("output_path", defaultValue=" "),
                                              file_dialog_title="Save playblast as",
                                              filters="*.mp4")
        self.output_viewer_checkbox = QtWidgets.QCheckBox("Open viewer")
        self.output_ornaments_checkbox = QtWidgets.QCheckBox("Show ornaments")
        self.output_offscreen_checkbox = QtWidgets.QCheckBox("Render offscreen")
        self.output_multicamera_checkbox = QtWidgets.QCheckBox("Multi-camera output")
        self.output_removetemp_checkbox = QtWidgets.QCheckBox("Removed temporary files")
        self.output_viewer_checkbox.setChecked(self.settings.value("output_viewer_checkbox_checked", defaultValue=True))
        self.output_ornaments_checkbox.setChecked(self.settings.value("output_offscreen_checkbox_checked", defaultValue=True))
        self.output_offscreen_checkbox.setChecked(self.settings.value("output_offscreen_checkbox_checked", defaultValue=False))
        self.output_multicamera_checkbox.setChecked(self.settings.value("output_multicamera_checkbox_checked", defaultValue=False))
        self.output_removetemp_checkbox.setChecked(self.settings.value("output_removetemp_checkbox_checked", defaultValue=True))

        # Buttons
        self.playblast_btn = QtWidgets.QPushButton("Playblast")

    def create_layouts(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.scroll_widget)
        self.scroll_widget.contentLayout.addWidget(self.ffmpeg_grp)
        self.scroll_widget.contentLayout.addWidget(self.image_grp)
        self.scroll_widget.contentLayout.addWidget(self.output_grp)
        self.main_layout.addWidget(self.playblast_btn)
        self.main_layout.setContentsMargins(5, 30, 5, 5)
        self.main_layout.setSpacing(2)

        self.ffmpeg_layout = QtWidgets.QVBoxLayout()
        self.ffmpeg_layout.addWidget(self.ffmpeg_path)
        self.ffmpeg_grp.setLayout(self.ffmpeg_layout)

        self.image_layout = QtWidgets.QVBoxLayout()
        self.image_layout.addWidget(self.image_mode)
        self.image_layout.addWidget(self.image_quality)
        self.image_layout.addWidget(self.image_scale)
        self.image_layout.addWidget(self.image_frame_padding)
        self.image_grp.setLayout(self.image_layout)

        self.output_layout = QtWidgets.QVBoxLayout()
        self.output_layout.addWidget(self.output_path)
        self.output_layout.addWidget(self.output_ornaments_checkbox)
        self.output_layout.addWidget(self.output_removetemp_checkbox)
        self.output_layout.addWidget(self.output_offscreen_checkbox)
        self.output_layout.addWidget(self.output_multicamera_checkbox)
        self.output_grp.setLayout(self.output_layout)

    def create_connections(self):
        pass
