import json
import os


def load_config():

    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    config_path = os.path.join(
        base_dir,
        "config.json"
    )

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"config.json not found:\n{config_path}"
        )

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as f:

        config = json.load(f)

    return config