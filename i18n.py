import json
from pathlib import Path
from typing import Dict, List

LOCALES_DIR = Path(__file__).parent / "locales"
DEFAULT_LANGUAGE = "en"

# Supported languages
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Español",
    "ru": "Русский",
}


class I18n:
    def __init__(self, locales_dir: Path = LOCALES_DIR, default_language: str = DEFAULT_LANGUAGE):
        self.locales_dir = locales_dir
        self.default_language = default_language
        self.current_language = default_language
        self._cache: Dict[str, Dict[str, str]] = {}
        self._load_language(default_language)

    def available_languages(self) -> List[str]:
        """Return language codes for every .json file found."""
        if not self.locales_dir.exists():
            return [self.default_language]
        codes = sorted(p.stem for p in self.locales_dir.glob("*.json"))
        return codes or [self.default_language]

    def display_name(self, lang_code: str) -> str:
        return LANGUAGE_NAMES.get(lang_code, lang_code)

    def _load_language(self, lang_code: str) -> Dict[str, str]:
        if lang_code in self._cache:
            return self._cache[lang_code]

        path = self.locales_dir / f"{lang_code}.json"
        if not path.exists():
            if lang_code != self.default_language:
                return self._load_language(self.default_language)
            return {}

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._cache[lang_code] = data
        return data

    def set_language(self, lang_code: str):
        self._load_language(lang_code)
        self.current_language = lang_code

    def t(self, key: str, **kwargs) -> str:
        """Translate key"""
        strings = self._load_language(self.current_language)
        text = strings.get(key)

        # Fallback to English
        if text is None:
            fallback = self._load_language(self.default_language)
            text = fallback.get(key, key)

        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        return text


i18n = I18n()


def t(key: str, **kwargs) -> str:
    """Shorthand for i18n.t()"""
    return i18n.t(key, **kwargs)
