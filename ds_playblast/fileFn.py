"""Common file operations"""
import pymel.core as pm
import json
from ds_playblast import Logger


def module_dir():
    return pm.moduleInfo(mn="ds_playblast", p=1)


# Json
def write_json(path, data={}, as_string=False, sort_keys=True):
    try:
        with open(path, "w") as json_file:
            if as_string:
                json_file.write(json.dumps(data, sort_keys=sort_keys, indent=4, separators=(",", ":")))
            else:
                json.dump(data, json_file, indent=4)

    except IOError as e:
        Logger.exception("{0} is not a valid file path".format(path), exc_info=e)
        return None

    except BaseException:
        Logger.exception("Failed to write file {0}".format(path), exc_info=1)
        return None

    return path


def load_json(path, string_data=False):
    try:
        with open(path, "r") as json_file:
            if string_data:
                data = json.loads(json_file)  # type:str
            else:
                data = json.load(json_file)  # type:dict

    except IOError:
        Logger.exception("{0} is not a valid file path".format(path))
        return None
    except BaseException:
        Logger.exception("Failed to load file {0}".format(path))
        return None

    return data  # type:dict
