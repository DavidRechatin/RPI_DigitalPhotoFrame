#!/usr/bin/python3

import yaml
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Internal configuration of the application"""
    user_config_file: str = "./user_config.yaml"
    path_media: str = "/home/pi/photos/"
    http_port: int = 8081


class UserConfig:
    """User's configuration. Can be changed during runtime."""
    display_time_in_sec: int = 5
    random_order: bool = False
    debug: bool = False

    @classmethod
    def load_from_file(cls):
        """Loads user-defined configuration items saved in user_config_file
        Returns:
            The attributes of the class are directly updated.
        """
        try:
            with open(AppConfig.user_config_file, 'r') as f:
                c = yaml.load(f, Loader=yaml.FullLoader)
                for (field, value) in c.items():
                    setattr(cls, field, value)
        except FileNotFoundError:
            print(
                f"Le fichier de configuration de l'utilisateur n'a pas été trouvé ({AppConfig.user_config_file}). "
                f"Les valeurs par défaut ont été conservées.")
            pass
