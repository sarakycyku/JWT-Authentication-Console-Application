# JWT-Authentication-Console-Application

## Setup

Krijo dhe aktivizo virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalo paketat e nevojshme:

```powershell
pip install -r requirements.txt
```

## Krijimi i `.pem` files

Projekti i krijon automatikisht `.pem` files kur startohet serveri:

```powershell
python server.py
```

Gjate startimit, serveri thirr funksionet `ensure_jwt_keys()` dhe `ensure_tls_certificate()` nga `jws_utils.py`.

`ensure_jwt_keys()` krijon celesat per JWT:

```text
private_key.pem
public_key.pem
```

`ensure_tls_certificate()` krijon certifikaten dhe celesin per TLS:

```text
server_cert.pem
server_cert_key.pem
```

Keto `.pem` files vendosen ne `.gitignore` sepse permbajne celesa privat/certifikata qe gjenerohen lokalisht dhe nuk duhet te ruhen apo shperndahen ne GitHub per arsye sigurie.

Nese deshiron me i kriju vetem keto files pa e lene serverin hapur, ekzekuto:

```powershell
python -c "from jws_utils import ensure_jwt_keys, ensure_tls_certificate; ensure_jwt_keys(); ensure_tls_certificate(); print('pem files created')"
```
