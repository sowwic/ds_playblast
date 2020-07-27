import os
import logging

LOGGER = logging.getLogger()


class Converter(object):
    def __init__(self, ffmpeg_path: str, input_path: str, output_path: str = ""):
        self.ffmpeg_path = ffmpeg_path
        self.input_path = input_path
        self.output_path = output_path

    def convert_avi_to_mp4(self):
        if not self.output_path or not self.output_path.endswith(".mp4"):
            self.output_path = self.input_path.replace(".avi", ".mp4")
        command = f'"{self.ffmpeg_path}" -i {self.input_path} {self.output_path} -y'
        return os.system(command)
