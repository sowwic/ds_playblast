import os
import pymel.core as pm
import pymel.api as pma

from PySide2 import QtWidgets
from PySide2 import QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import getCppPointer

from ds_playblast import Logger
from ds_playblast import Config
import qt_widgets_lib.py2 as widgets_lib
import ds_playblast.playblastFn as playblastFn
Logger.write_to_rotating_file("playblast.log")


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "dsPlayblast"
    UI_NAME = "dsPlayblast"
    UI_SCRIPT = "import ds_playblast\nds_playblast.MainDialog()"
    UI_INSTANCE = None

    playblasting = QtCore.Signal(bool)

    @classmethod
    def display(cls):
        if not cls.UI_INSTANCE:
            cls.UI_INSTANCE = MainDialog()

        if cls.UI_INSTANCE.isHidden():
            cls.UI_INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.UI_INSTANCE.raise_()
            cls.UI_INSTANCE.activateWindow()

    def hideEvent(self, event):
        self.save_config()
        super(MainDialog, self).hideEvent(event)

    def __init__(self):
        super(MainDialog, self).__init__()
        self.sizes_buffer = []

        self.__class__.UI_INSTANC = self
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(300, 165)

        # Workspace control
        workspace_control_name = "{0}WorkspaceControl".format(self.UI_NAME)
        if pm.workspaceControl(workspace_control_name, q=1, ex=1):
            workspace_control_ptr = long(pma.MQtUtil.findControl(workspace_control_name))
            widget_ptr = long(getCppPointer(self)[0])
            pma.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.load_config()

    def create_actions(self):
        pass

    def create_widgets(self):
        # Container widgets
        self.scroll_wgt = widgets_lib.ScrollWidget()
        self.vert_splitter = QtWidgets.QSplitter()
        self.vert_splitter.setOrientation(QtCore.Qt.Vertical)
        # Time
        self.time_range_wgt = widgets_lib.TimeRangeWidget(title="Time", mode=1, range_func=playblastFn.get_playback_range)
        # Image group
        self.image_grp = QtWidgets.QGroupBox("Image")
        self.resolutions_box = QtWidgets.QComboBox()
        for item in playblastFn.RESOLUTIONS:
            self.resolutions_box.addItem(item[0], item[1])

        self.quality_field = widgets_lib.SliderFieldWidget(data_type="int", label_text="Quality:", min_value=0, max_value=100, default_value=100)
        self.scale_field = widgets_lib.SliderFieldWidget(data_type="float", label_text="Scale:", min_value=0.1, max_value=1.0, default_value=1.0, step=0.1, slider_multiplier=100.0)
        self.padding_field = widgets_lib.SliderFieldWidget(data_type="int", label_text="Frame padding:", min_value=0, max_value=4, default_value=4)
        # Output group
        self.output_grp = QtWidgets.QGroupBox("Output")
        self.out_file_path = widgets_lib.PathWidget(mode="save_file",
                                                    label_text="Output file:",
                                                    dialog_label="Set output file path",
                                                    file_filters="MP4 video (*.mp4)",
                                                    selected_filter="MP4 video (*.mp4)")
        self.open_viewer_option = QtWidgets.QCheckBox("Open viewer")
        self.ornaments_option = QtWidgets.QCheckBox("Show ornaments")
        self.remove_temp_option = QtWidgets.QCheckBox("Remove temporary files")
        self.offscreen_option = QtWidgets.QCheckBox("Render offscreen")
        self.clear_cache_option = QtWidgets.QCheckBox("Clear cache")
        # Other
        self.run_playblast_btn = QtWidgets.QPushButton("Playblast")
        self.logger_output = QtWidgets.QPlainTextEdit()
        self.logger_output.setReadOnly(True)

    def create_layouts(self):
        image_layout = QtWidgets.QVBoxLayout()
        image_layout.addWidget(self.resolutions_box)
        image_layout.addWidget(self.quality_field)
        image_layout.addWidget(self.scale_field)
        image_layout.addWidget(self.padding_field)
        self.image_grp.setLayout(image_layout)

        output_layout = QtWidgets.QVBoxLayout()
        output_layout.addWidget(self.out_file_path)
        output_layout.addWidget(self.open_viewer_option)
        output_layout.addWidget(self.ornaments_option)
        output_layout.addWidget(self.remove_temp_option)
        output_layout.addWidget(self.offscreen_option)
        output_layout.addWidget(self.clear_cache_option)
        self.output_grp.setLayout(output_layout)

        self.scroll_wgt.add_widget(self.time_range_wgt)
        self.scroll_wgt.add_widget(self.image_grp)
        self.scroll_wgt.add_widget(self.output_grp)
        self.scroll_wgt.add_stretch()

        self.vert_splitter.addWidget(self.scroll_wgt)
        self.vert_splitter.addWidget(self.logger_output)
        self.vert_splitter.setSizes([300, 0])

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.vert_splitter)
        self.main_layout.addWidget(self.run_playblast_btn)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.run_playblast_btn.clicked.connect(self.run_playblast)
        Logger.signal_handler().emitter.message_logged.connect(self.logger_output.appendPlainText)
        self.playblasting.connect(self.update_splitter)

    def load_config(self):
        config_dict = Config.load()
        self.resolutions_box.setCurrentIndex(config_dict.get("image.resolution", 3))
        self.quality_field.set_value(config_dict.get("image.quality", 100))
        self.scale_field.set_value(config_dict.get("image.scale", 1.0))
        self.padding_field.set_value(config_dict.get("image.fpadding", 4))
        self.out_file_path.set_path(config_dict.get("out.path", ""))
        self.open_viewer_option.setChecked(config_dict.get("out.viewer", True))
        self.ornaments_option.setChecked(config_dict.get("out.ornaments", True))
        self.remove_temp_option.setChecked(config_dict.get("out.remove_temp", True))
        self.offscreen_option.setChecked(config_dict.get("out.offscreen", False))
        self.clear_cache_option.setChecked(config_dict.get("out.clear_cache", True))

    def save_config(self):
        new_config = {}
        new_config["image.resolution"] = self.resolutions_box.currentIndex()
        new_config["image.quality"] = self.quality_field.value
        new_config["image.scale"] = self.scale_field.value
        new_config["image.fpadding"] = self.padding_field.value
        new_config["out.path"] = self.out_file_path.path
        new_config["out.viewer"] = self.open_viewer_option.isChecked()
        new_config["out.ornaments"] = self.ornaments_option.isChecked()
        new_config["out.remove_temp"] = self.remove_temp_option.isChecked()
        new_config["out.offscreen"] = self.offscreen_option.isChecked()
        new_config["out.clear_cache"] = self.clear_cache_option.isChecked()
        Config.update(new_config)

    def update_splitter(self, is_playblasting):
        if is_playblasting:
            self.sizes_buffer = self.vert_splitter.sizes()
            if not self.sizes_buffer[1]:
                self.vert_splitter.setSizes([self.sizes_buffer[0], 200])
        else:
            self.vert_splitter.setSizes(self.sizes_buffer)

    def run_playblast(self):
        self.playblasting.emit(True)
        output_path = self.out_file_path.path  # type: str
        if not os.path.isdir(os.path.dirname(output_path)):
            Logger.error("Invalid output file: {0}".format(output_path))
            return

        self.logger_output.clear()
        avi_path = output_path.replace(".mp4", ".avi")
        time_range = self.time_range_wgt.get_range()
        Logger.info("Running playblast...")
        pm.playblast(f=avi_path,
                     cc=self.clear_cache_option.isChecked(),
                     orn=self.ornaments_option.isChecked(),
                     qlt=self.quality_field.value,
                     os=self.offscreen_option.isChecked(),
                     fp=self.padding_field.value,
                     h=self.resolutions_box.currentData()[1],
                     w=self.resolutions_box.currentData()[0],
                     p=self.scale_field.value * 100,
                     st=time_range[0],
                     et=time_range[1],
                     v=False,
                     fmt="avi",
                     fo=1)
        Logger.info("Converting to mp4...")
        playblastFn.convert_avi_to_mp4(avi_path, output_path)
        # Cleanup
        os.remove(avi_path)
        if self.open_viewer_option.isChecked():
            os.startfile(output_path)
        Logger.info("Done.")
        self.playblasting.emit(False)


if __name__ == "__main__":
    try:
        if playblast_window and playblast_window.parent():  # noqa: F821
            workspace_control_name = playblast_window.parent().objectName()  # noqa: F821

            if pm.window(workspace_control_name, ex=1, q=1):
                pm.deleteUI(workspace_control_name)
    except Exception:
        pass

    playblast_window = MainDialog()
    playblast_window.show(dockable=1, uiScript="")
