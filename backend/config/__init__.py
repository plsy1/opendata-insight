import os
import yaml
import base64
from threading import Lock

from app_paths import CONFIG_PATH, IMAGE_CACHE_DIR


class ConfigManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if config_path is None:
                        config_path = str(CONFIG_PATH)
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
        self.config.setdefault("AVBASE_ACTOR_CACHE_HOURS", 24)
        self.config.setdefault("AVBASE_MAX_CONCURRENCY", 4)
        self.config.setdefault("AVBASE_HTTP_TIMEOUT_SECONDS", 10)
        self.config.setdefault("AVBASE_HTTP_RETRIES", 1)
        self.config.setdefault("AVBASE_RELEASE_RETENTION_DAYS", 30)
        legacy_required = self.config.get("SUBSCRIBE_TITLE_REQUIRED", [])
        legacy_any = self.config.get("SUBSCRIBE_TITLE_ANY", [])
        legacy_excluded = self.config.get("SUBSCRIBE_TITLE_EXCLUDED", [])
        legacy_regex = self.config.get("SUBSCRIBE_TITLE_REGEX", "")
        self.config.setdefault("SUBSCRIBE_GLOBAL_EXCLUDED", legacy_excluded)
        if "SUBSCRIBE_QUALITY_RULES" not in self.config:
            legacy_resolutions = self.config.get("SUBSCRIBE_RESOLUTIONS", [])
            legacy_codecs = self.config.get("SUBSCRIBE_CODECS", [])
            if isinstance(legacy_resolutions, str):
                legacy_resolutions = legacy_resolutions.split(",")
            if isinstance(legacy_codecs, str):
                legacy_codecs = legacy_codecs.split(",")
            self.config["SUBSCRIBE_QUALITY_RULES"] = (
                [
                    {"resolution": resolution or None, "codec": codec or None}
                    for resolution in (legacy_resolutions or [None])
                    for codec in (legacy_codecs or [None])
                ]
                if legacy_resolutions or legacy_codecs
                else []
            )
        quality_rules = self.config.get("SUBSCRIBE_QUALITY_RULES", [])
        legacy_group_filter = bool(legacy_required or legacy_any or legacy_regex)
        if not quality_rules and legacy_group_filter:
            quality_rules = [{"resolution": None, "codec": None}]
        if legacy_group_filter and quality_rules and all(
            isinstance(rule, dict)
            and not any(
                key in rule
                for key in (
                    "required_keywords",
                    "any_keywords",
                    "excluded_keywords",
                    "title_regex",
                )
            )
            for rule in quality_rules
        ):
            for rule in quality_rules:
                rule.update(
                    {
                        "required_keywords": legacy_required,
                        "any_keywords": legacy_any,
                        "excluded_keywords": [],
                        "title_regex": legacy_regex,
                    }
                )
        self.config["SUBSCRIBE_QUALITY_RULES"] = quality_rules
        self.config.setdefault("SECRET_KEY", "change-me")
        self.config.setdefault("ALGORITHM", "HS256")
        self.config.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)
        self.config.setdefault("IMAGE_AUTH_COOKIE", "image_access")
        self.config.setdefault("IMAGE_COOKIE_SECURE", False)
        self.config.setdefault("IMAGE_CACHE_HOURS", 168)
        self.config.setdefault("IMAGE_MAX_CONCURRENCY", 8)
        self.config.setdefault("IMAGE_HTTP_TIMEOUT_SECONDS", 20)
        self.config.setdefault("IMAGE_MAX_BYTES", 25 * 1024 * 1024)
        self.config.setdefault(
            "IMAGE_TOKEN_SECRET", base64.urlsafe_b64encode(os.urandom(32)).decode()
        )

        self.config["CACHE_DIR"] = str(IMAGE_CACHE_DIR)
        self.config["SYSTEM_IMAGE_PREFIX"] = "/api/v1/system/images/"

    def get(self, key: str, default=""):
        return self.config.get(key, os.environ.get(key, default))

    def get_bool(self, key: str, default=False) -> bool:
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    def set(self, new_config: dict):
        self.config.update(new_config)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, allow_unicode=True)

    def get_download_path(self, media_type: str | None = None) -> str:
        """Return a media-specific path, falling back to the legacy default."""
        media_key = {
            "jav": "JAV_DOWNLOAD_PATH",
            "fc2": "FC2_DOWNLOAD_PATH",
        }.get(str(media_type or "").strip().casefold())
        if media_key:
            configured = str(self.get(media_key, "") or "").strip()
            if configured:
                return configured
        return str(self.get("DOWNLOAD_PATH", "") or "").strip()

    def get_environment(self):
        """
        返回当前环境变量配置，用于前端显示或修改
        """
        return {
            "PROWLARR_URL": self.config.get("PROWLARR_URL", ""),
            "PROWLARR_KEY": self.config.get("PROWLARR_KEY", ""),
            "DOWNLOAD_PATH": self.config.get("DOWNLOAD_PATH", ""),
            "JAV_DOWNLOAD_PATH": self.config.get("JAV_DOWNLOAD_PATH", ""),
            "FC2_DOWNLOAD_PATH": self.config.get("FC2_DOWNLOAD_PATH", ""),
            "QB_URL": self.config.get("QB_URL", ""),
            "QB_USERNAME": self.config.get("QB_USERNAME", ""),
            "QB_PASSWORD": self.config.get("QB_PASSWORD", ""),
            "QB_KEYWORD_FILTER": self.config.get(
                "QB_KEYWORD_FILTER", ["游戏大全", "七龍珠"]
            ),
            "SUBSCRIBE_GLOBAL_EXCLUDED": self.config.get(
                "SUBSCRIBE_GLOBAL_EXCLUDED", []
            ),
            "SUBSCRIBE_QUALITY_RULES": self.config.get(
                "SUBSCRIBE_QUALITY_RULES", []
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
