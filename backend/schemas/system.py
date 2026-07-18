import json
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_keyword_list(value) -> list[str]:
    if not isinstance(value, str):
        return value or []

    text = value.strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = [part.strip() for part in re.split(r"[,，;；\n]", text)]
    if isinstance(parsed, str):
        parsed = [parsed]
    return [str(item).strip() for item in parsed if str(item).strip()]


class SubscriptionQualityRuleConfig(BaseModel):
    resolution: Optional[str] = None
    codec: Optional[str] = None
    required_keywords: list[str] = Field(default_factory=list)
    any_keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)
    title_regex: str = ""

    @field_validator("resolution", "codec", mode="before")
    @classmethod
    def _normalize_optional_value(cls, value):
        normalized = str(value or "").strip()
        return normalized or None

    @field_validator(
        "required_keywords",
        "any_keywords",
        "excluded_keywords",
        mode="before",
    )
    @classmethod
    def _normalize_keywords(cls, value):
        return _normalize_keyword_list(value)

    @field_validator("title_regex")
    @classmethod
    def _validate_title_regex(cls, value: str) -> str:
        pattern = value.strip()
        if pattern:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as exc:
                raise ValueError(f"Invalid subscription title regex: {exc}") from exc
        return pattern


class EnvironmentConfig(BaseModel):
    PROWLARR_URL: str = ""
    PROWLARR_KEY: str = ""
    DOWNLOAD_PATH: str = ""
    JAV_DOWNLOAD_PATH: str = ""
    FC2_DOWNLOAD_PATH: str = ""
    QB_URL: str = ""
    QB_USERNAME: str = ""
    QB_PASSWORD: str = ""
    QB_KEYWORD_FILTER: list[str] = Field(default_factory=list)
    SUBSCRIBE_GLOBAL_EXCLUDED: list[str] = Field(default_factory=list)
    SUBSCRIBE_QUALITY_RULES: list[SubscriptionQualityRuleConfig] = Field(
        default_factory=list
    )
    TELEGRAM_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    EMBY_URL: str = ""
    EMBY_API_KEY: str = ""

    model_config = {"extra": "allow"}

    @field_validator(
        "QB_KEYWORD_FILTER",
        "SUBSCRIBE_GLOBAL_EXCLUDED",
        mode="before",
    )
    @classmethod
    def _normalize_keyword_filter(cls, value):
        return _normalize_keyword_list(value)

    @field_validator("SUBSCRIBE_QUALITY_RULES", mode="before")
    @classmethod
    def _normalize_quality_rules(cls, value):
        if not value:
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Subscription quality rules must be valid JSON"
                ) from exc
        if not isinstance(value, list):
            raise ValueError("Subscription quality rules must be a list")
        return value

class VersionOut(BaseModel):
    version: str


class UpdateCheckOut(BaseModel):
    latest_version: Optional[str] = None
