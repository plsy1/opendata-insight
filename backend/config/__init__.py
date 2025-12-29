import os
import sys
import yaml
import base64
from threading import Lock


class ConfigManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if config_path is None:
                        main_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                        config_path = os.path.join(main_dir, "data", "config.yaml")
                    cls._instance = super().__new__(cls)
                    cls._instance._init(config_path)
        return cls._instance

    def _init(self, config_path: str):
        self.config_path = config_path
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

        self.config.setdefault("CACHE_EXPIRE_HOURS", 24)
        self.config.setdefault("SECRET_KEY", "change-me")
        self.config.setdefault("ALGORITHM", "HS256")
        self.config.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)
        self.config.setdefault(
            "IMAGE_TOKEN_SECRET", base64.urlsafe_b64encode(os.urandom(32)).decode()
        )

        main_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.config["CACHE_DIR"] = os.path.join(main_dir, "data/cache_images")
        self.config["SYSTEM_IMAGE_PREFIX"] = "/api/v1/system/get_image?token="

    def get(self, key: str, default=""):
        return self.config.get(key, os.environ.get(key, default))

    def set(self, new_config: dict):
        self.config.update(new_config)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, allow_unicode=True)

    def get_environment(self):
        """
        返回当前环境变量配置，用于前端显示或修改
        """
        return {
            "PROWLARR_URL": self.config.get("PROWLARR_URL", ""),
            "PROWLARR_KEY": self.config.get("PROWLARR_KEY", ""),
            "DOWNLOAD_PATH": self.config.get("DOWNLOAD_PATH", ""),
            "QB_URL": self.config.get("QB_URL", ""),
            "QB_USERNAME": self.config.get("QB_USERNAME", ""),
            "QB_PASSWORD": self.config.get("QB_PASSWORD", ""),
            "QB_KEYWORD_FILTER": self.config.get(
                "QB_KEYWORD_FILTER", ["游戏大全", "七龍珠"]
            ),
            "TELEGRAM_TOKEN": self.config.get("TELEGRAM_TOKEN", ""),
            "TELEGRAM_CHAT_ID": self.config.get("TELEGRAM_CHAT_ID", ""),
            "EMBY_URL": self.config.get("EMBY_URL", ""),
            "EMBY_API_KEY": self.config.get("EMBY_API_KEY", ""),
        }

    def get_image_token_key(self) -> bytes:
        key = self.get("IMAGE_TOKEN_SECRET")
        return base64.urlsafe_b64decode(key)


_config = ConfigManager()
