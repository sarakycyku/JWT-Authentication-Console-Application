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

def authenticate(username: str, password: str) -> bool:
    user = USERS.get(username)
    if not user:
        return False
    salt = base64.b64decode(user["salt"])
    candidate_hash = hash_password(password, salt)
    return hmac.compare_digest(candidate_hash, user["password_hash"])

def handle_login(request: dict[str, Any]) -> dict[str, Any]:
    username = str(request.get("username", ""))
    password = str(request.get("password", ""))
    print("Credentials received. Verifying...")

    if not authenticate(username, password):
        print("Authentication failed.")
        return {"status": 401, "error": "Unauthorized: invalid username or password"}

    token = create_token(username)
    print("Authentication successful. JWT issued.")
    return {"status": 200, "message": "Logged in", "token": token}

def handle_protected_data(request: dict[str, Any]) -> dict[str, Any]:
    auth_header = str(request.get("authorization", ""))
    if not auth_header.startswith("Bearer "):
        return {"status": 401, "error": "Unauthorized: missing bearer token"}

    token = auth_header.removeprefix("Bearer ").strip()
    try:
        claims = validate_token(token)
    except jwt.ExpiredSignatureError:
        return {"status": 401, "error": "Unauthorized: token expired"}
    except jwt.InvalidTokenError:
        return {"status": 401, "error": "Unauthorized: invalid token"}

    return {
        "status": 200,
        "data": "This is protected data.",
        "authenticated_user": claims["sub"],
    }
def route_request(request: dict[str, Any]) -> dict[str, Any]:
    command = request.get("command")
    if command == "login":
        return handle_login(request)
    if command == "protected-data":
        return handle_protected_data(request)
    if command == "logout":
        return {"status": 200, "message": "Logged out"}
    return {"status": 400, "error": "Bad request: unknown command"}
def handle_client(client_socket: ssl.SSLSocket, address: tuple[str, int]) -> None:
    print(f"Connection established from {address}. Awaiting request...")
    try:
        request = receive_json(client_socket)
        response = route_request(request)
        send_json(client_socket, response)
    except (json.JSONDecodeError, ValueError) as exc:
        send_json(client_socket, {"status": 400, "error": f"Bad request: {exc}"})
    except OSError as exc:
        print(f"Connection error: {exc}")
    except Exception as exc:
        print(f"Unexpected server error while handling {address}: {exc}")
        traceback.print_exc()
        try:
            send_json(client_socket, {"status": 500, "error": "Internal server error"})
        except OSError:
            pass
    finally:
        client_socket.close()
def start_server() -> None:
    ensure_jwt_keys()
    ensure_tls_certificate()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SERVER_CERT_PATH, keyfile=SERVER_CERT_KEY_PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server: Waiting for connections on {HOST}:{PORT}...")

        while True:
            raw_client, address = server_socket.accept()
            try:
                client_socket = context.wrap_socket(raw_client, server_side=True)
            except ssl.SSLError as exc:
                print(f"TLS handshake failed: {exc}")
                raw_client.close()
                continue
            threading.Thread(target=handle_client, args=(client_socket, address), daemon=True).start()