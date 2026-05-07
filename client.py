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