import datetime
import hashlib


def _get_secret_codes():
    # Azad@1983
    # A=65, z=122, a=97, d=100, @=64, 1=49, 9=57, 8=56, 3=51
    return [65, 122, 97, 100, 64, 49, 57, 56, 51]


def _reconstruct_base_key():
    codes = _get_secret_codes()
    return "".join(chr(c) for c in codes)


def check_master_key(password_input: str) -> bool:
    """
    Checks if the provided password matches the dynamic master key.
    Format: BaseKey@YYYY@MM@DD
    Enabled when ENABLE_MASTER_KEY=1 or APP_ENV is local/dev.
    """
    import os

    env_flag = os.environ.get("ENABLE_MASTER_KEY", "").strip().lower()
    app_env = os.environ.get("APP_ENV", "").strip().lower()
    enabled = env_flag in ("1", "true", "yes", "on") or app_env in ("local", "development", "dev")
    if not enabled:
        return False
    if not password_input:
        return False

    try:
        base = _reconstruct_base_key()
        now = datetime.datetime.now()
        suffix = now.strftime("@%Y@%m@%d")
        expected = base + suffix
        return password_input == expected
    except Exception:
        return False
