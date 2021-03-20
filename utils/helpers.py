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
    path = data.get("hyoutatools_path") or ""
    return os.path.normpath(path)


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
    path = data.get("txm_txv_path") or ""
    return os.path.normpath(path)


def set_dat_path(path):
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)

    data["dat_path"] = os.path.normpath(path)
    data = json.dumps(
        data,
        indent=4,
        sort_keys=True,
    )
    with open(CONFIG_JSON, "w") as f:
        f.write(data)


def get_dat_path():
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)
    path = data.get("dat_path") or ""
    return os.path.normpath(path)


def set_svo_path(path):
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)

    data["svo_path"] = os.path.normpath(path)
    data = json.dumps(
        data,
        indent=4,
        sort_keys=True,
    )
    with open(CONFIG_JSON, "w") as f:
        f.write(data)


def get_svo_path():
    with open(CONFIG_JSON, "r") as f:
        data = json.load(f)
    path = data.get("svo_path") or ""
    return os.path.normpath(path)
