from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = BASE_DIR / "private_key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "public_key.pem"
SERVER_CERT_PATH = BASE_DIR / "server_cert.pem"
SERVER_CERT_KEY_PATH = BASE_DIR / "server_cert_key.pem"

JWT_ISSUER = "jwt-console-server"
JWT_AUDIENCE = "jwt-console-client"
JWT_ALGORITHM = "RS256"
JWT_TTL_MINUTES = 15


def ensure_jwt_keys() -> None:
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    PRIVATE_KEY_PATH.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    PUBLIC_KEY_PATH.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def ensure_tls_certificate() -> None:
    if SERVER_CERT_PATH.exists() and SERVER_CERT_KEY_PATH.exists():
        return

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "XK"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "JWT Console Demo"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        .sign(key, hashes.SHA256())
    )

    SERVER_CERT_KEY_PATH.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    SERVER_CERT_PATH.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def create_token(username: str, role: str) -> str:
    ensure_jwt_keys()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_TTL_MINUTES),
    }
    private_key = PRIVATE_KEY_PATH.read_text(encoding="utf-8")
    return jwt.encode(payload, private_key, algorithm=JWT_ALGORITHM)


def validate_token(token: str) -> dict:
    public_key = PUBLIC_KEY_PATH.read_text(encoding="utf-8")
    return jwt.decode(
        token,
        public_key,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
    )
