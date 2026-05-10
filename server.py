from __future__ import annotations

import base64
import hashlib
import hmac
import json
import socket
import ssl
import threading
import traceback
from typing import Any

import jwt

from jwt_utils import (
    SERVER_CERT_KEY_PATH,
    SERVER_CERT_PATH,
    create_token,
    ensure_jwt_keys,
    ensure_tls_certificate,
    validate_token,
)


HOST = "127.0.0.1"
PORT = 5050


def hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return base64.b64encode(digest).decode("ascii")


def make_user_record(password: str) -> dict[str, str]:
    salt = hashlib.sha256(password.encode("utf-8")).digest()[:16]
    return {
        "salt": base64.b64encode(salt).decode("ascii"),
        "password_hash": hash_password(password, salt),
    }


USERS = {
    "admin": make_user_record("admin123"),
    "sara": make_user_record("sara123"),
    "andi": make_user_record("andi123"),
    "rubeja": make_user_record("ruveja123"),
}
