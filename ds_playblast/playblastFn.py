import os
import platform
try:
    from StringIO import StringIO  # for Python 2
except ImportError:
    from io import StringIO  # for Python 3
import pymel.core as pm

from ds_playblast import Logger
from ds_playblast import Config
import ds_playblast.fileFn as fileFn


RESOLUTIONS = [["320x480", (320, 480)],
               ["640x480", (640, 480)],
               ["HD_540", (960, 540)],
               ["HD_720", (1280, 720)],
               ["HD_1080", (1920, 1080)]]


def get_playback_range():
    time_range = (int(pm.playbackOptions(min=1, q=1)), int(pm.playbackOptions(max=1, q=1)))
    return time_range


def get_ffmpeg_path():
    ffmpeg = Config.get("ffmpeg_path", "")
    if not ffmpeg:
        if platform.system() == "Windows":
            ffmpeg = os.path.join(fileFn.module_dir(), "tools", "ffmpeg.exe")
        Config.set("ffmpeg_path", ffmpeg)
    return ffmpeg


def convert_avi_to_mp4(input_path, output_path):
    Logger.info("File accessible: {0}".format(os.access(input_path, os.X_OK)))
    cmd_args = [get_ffmpeg_path(), "-i", input_path, output_path, "-y"]
    ffmpeg_process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for std_out_line in iter(ffmpeg_process.stdout.readline, ""):
        Logger.info(std_out_line.strip())
    ffmpeg_process.stdout.close()
    return_code = ffmpeg_process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd_args)
