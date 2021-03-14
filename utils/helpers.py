import json
import os

from constants.path import CONFIG_JSON


def create_config_json():
    with open(CONFIG_JSON, "w") as f:
        data = json.dumps(
            {
                "hyoutatools_path": "",
                "txm_txv_path": "",
            },
            indent=4,
            sort_keys=True,
        )
        f.write(data)


def set_hyoutatools_path(path):
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)

    data["hyoutatools_path"] = os.path.normpath(path)
    data = json.dumps(
       data,
        indent=4,
        sort_keys=True,
    )
    with open(CONFIG_JSON, "w") as f:
        f.write(data)


def get_hyoutatools_path():
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)
    return os.path.normpath(data["hyoutatools_path"])


def set_txm_txm_path(path):
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)

    data["txm_txv_path"] = os.path.normpath(path)
    data = json.dumps(
        data,
        indent=4,
        sort_keys=True,
    )
    with open(CONFIG_JSON, "w") as f:
        f.write(data)


def get_txm_txv_path():
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)
    return os.path.normpath(data["txm_txv_path"])
