from __future__ import annotations

import json
import msvcrt
import socket
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jwt

from jwt_utils import (
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    JWT_ISSUER,
    PUBLIC_KEY_PATH,
    SERVER_CERT_PATH,
)

HOST = "127.0.0.1"
PORT = 5050


def read_password(prompt: str = "Enter password: ") -> str:
    """Lexon password-in pa e shfaqur në console (Windows)."""
    print(prompt, end="", flush=True)
    chars: list[str] = []

    while True:
        char = msvcrt.getwch()
        if char in ("\r", "\n"):
            print()
            return "".join(chars)
        if char == "\003":
            raise KeyboardInterrupt
        if char == "\b":
            if chars:
                chars.pop()
                print("\b \b", end="", flush=True)
            continue

        chars.append(char)
        print("*", end="", flush=True)