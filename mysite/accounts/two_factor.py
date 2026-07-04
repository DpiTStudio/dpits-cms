# accounts/two_factor.py
"""Утилиты для работы с двухфакторной аутентификацией (TOTP).

Модуль использует библиотеку `pyotp` для генерации секретов, расчёта
одноразовых кодов и формирования URL, совместимого с приложениями
Google Authenticator, Authy и другими.
"""

import logging
from urllib.parse import quote

import pyotp

logger = logging.getLogger(__name__)


def generate_totp_secret():
    """Создать новый базовый32‑секрет для TOTP.

    Возвращает строку, которую можно сохранить в модели профиля
    (например, `UserProfile.totp_secret`).
    """
    secret = pyotp.random_base32()
    logger.info("Сгенерирован новый TOTP‑секрет: %s", secret)
    return secret


def get_totp_uri(username: str, issuer_name: str, secret: str) -> str:
    """Сформировать URI в формате `otpauth://`.

    Параметры:
        username – имя пользователя, будет отображено в приложении
        issuer_name – название сервиса (например, "MySite")
        secret – базовый32‑секрет, выданный `generate_totp_secret`

    Возвращает строку, которую можно передать в QR‑код или
    отобразить как обычную ссылку.
    """
    label = quote(f"{issuer_name}:{username}")
    issuer = quote(issuer_name)
    uri = f"otpauth://totp/{label}?secret={secret}&issuer={issuer}&algorithm=SHA1&digits=6&period=30"
    logger.debug("Сформирован TOTP URI: %s", uri)
    return uri


def verify_totp_token(secret: str, token: str) -> bool:
    """Проверить введённый пользователем токен.

    Параметры:
        secret – TOTP‑секрет, сохранённый в профиле
        token – строка из шести цифр, полученная из приложения

    Возвращает `True`, если токен корректен (с учётом небольшого окна).
    """
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(token, valid_window=1)
    logger.info("Проверка TOTP токена %s: %s", token, is_valid)
    return is_valid


def get_qr_code_url(totp_uri: str) -> str:
    """Возвратить URL к публичному сервису генерации QR‑кода.

    Встроенный сервис Google Chart API позволяет получить PNG‑картинку
    без дополнительных библиотек.
    """
    encoded = quote(totp_uri)
    url = f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={encoded}&choe=UTF-8"
    logger.debug("QR‑code URL: %s", url)
    return url
