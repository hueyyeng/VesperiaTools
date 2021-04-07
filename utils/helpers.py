import json
import os

from constants.path import CONFIG_JSON


def create_config_json():
    with open(CONFIG_JSON, "w") as f:
        data = json.dumps(
            {
                "hyoutatools_path": "",
                "txm_txv_path": "",
                "dat_path": "",
                "svo_path": "",
                "spm_spv_path": "",
                "obj_path": "",
            },
            indent=4,
            sort_keys=True,
        )
        f.write(data)


def set_path(config_key, path):
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)

    data[config_key] = os.path.normpath(path)
    data = json.dumps(
       data,
        indent=4,
        sort_keys=True,
    )
    with open(CONFIG_JSON, "w") as f:
        f.write(data)


def get_path(config_key):
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)
    path = data.get(config_key) or ""
    return os.path.normpath(path)


def set_hyoutatools_path(path):
    set_path("hyoutatools_path", path)


def set_txm_txm_path(path):
    set_path("txm_txv_path", path)


def set_dat_path(path):
    set_path("dat_path", path)


def set_svo_path(path):
    set_path("svo_path", path)


def set_spm_spv_path(path):
    set_path("spm_spv_path", path)


def set_mtr_path(path):
    set_path("mtr_path", path)


def set_obj_path(path):
    set_path("obj_path", path)
