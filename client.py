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
    """Lexon password-in pa e shfaqur ne console (Windows)."""
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


def send_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Dergon nje kerkese JSON te serveri permes TLS dhe kthen pergjigjen."""
    if not SERVER_CERT_PATH.exists():
        raise FileNotFoundError(
            "server_cert.pem mungon. Startoje serverin nje here qe ta gjeneroje certifikaten."
        )

    context = ssl.create_default_context(cafile=str(SERVER_CERT_PATH))
    context.check_hostname = False

    with socket.create_connection((HOST, PORT), timeout=10) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname="localhost") as sock:
            sock.sendall(json.dumps(payload).encode("utf-8") + b"\n")
            data = bytearray()
            while not data.endswith(b"\n"):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data.extend(chunk)

    if not data:
        raise ConnectionResetError("Server closed the connection without sending a response.")
    return json.loads(data.decode("utf-8"))


def print_token_summary(token: str) -> None:
    """Shfaq informata rreth token-it (sub, exp) nese public key ekziston."""
    if not PUBLIC_KEY_PATH.exists():
        return
    try:
        public_key = PUBLIC_KEY_PATH.read_text(encoding="utf-8")
        claims = jwt.decode(
            token,
            public_key,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except jwt.InvalidTokenError:
        return

    expires_at = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    print(f"Token valid for user '{claims['sub']}' until {expires_at.isoformat()}.")


def login() -> str | None:
    """Ben login te serveri dhe kthen token-in nese eshte i suksesshem."""
    while True:
        username = input("Enter username: ").strip()
        password = read_password("Enter password: ")
        response = send_request({"command": "login", "username": username, "password": password})

        if response.get("status") == 200:
            token = str(response["token"])
            print("Logged in. JWT token is:")
            print(token)
            print_token_summary(token)
            return token

        print(response.get("error", "Login failed"))
        while True:
            choice = input("1. Try again\n2. Quit\nChoose option: ").strip()
            if choice == "1":
                break
            if choice == "2":
                return None
            print("Invalid option.")


def request_protected_data(token: str | None) -> None:
    """Kerkon te dhenat e mbrojtura nga serveri duke perdorur token-in."""
    if not token:
        print("You are not logged in.")
        return

    print("Accessing protected data...")
    response = send_request(
        {
            "command": "protected-data",
            "authorization": f"Bearer {token}",
        }
    )
    if response.get("status") == 200:
        print("Protected data received:")
        print(json.dumps({"data": response["data"]}, indent=2))
    else:
        print(response.get("error", "Request failed"))


def logout(token: str | None) -> None:
    """Fshin token-in dhe perfundon sesionin."""
    if token:
        try:
            send_request({"command": "logout"})
        except OSError:
            pass
    print("Logging out...")


def main() -> None:
    """Funksioni kryesor i client-it."""
    token = login()
    if not token:
        return

    while True:
        command = input("Enter command ('request_data' or 'logout'): ").strip().lower()
        if command == "request_data":
            request_protected_data(token)
        elif command == "logout":
            logout(token)
            token = None
            break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClient stopped.")
    except ConnectionRefusedError:
        print("Could not connect to server on 127.0.0.1:5050.")
        print("Startoje serverin ne nje terminal tjeter me:")
        print(r".\.venv\Scripts\python.exe server.py")
    except TimeoutError:
        print("Connection timed out while contacting the server.")
    except ConnectionResetError as exc:
        print(f"Server connection was closed: {exc}")
    except OSError as exc:
        print(f"Connection error: {exc}")
    except json.JSONDecodeError:
        print("Server returned an invalid or incomplete response.")
    except FileNotFoundError as exc:
        print(exc)
