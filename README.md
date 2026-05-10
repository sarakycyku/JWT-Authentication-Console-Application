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

## Ekzekutimi

Starto serverin ne nje terminal:

```powershell
python server.py
```

Pastaj starto klientin ne nje terminal tjeter:

```powershell
python client.py
```

Serveri pret lidhje ne:

```text
127.0.0.1:5050
```

## Perdorimi

Kur startohet klienti, shkruaj username dhe password.

User-at testues:

```text
admin / admin123
sara / sara123
andi / andi123
rubeja / ruveja123
```

Pas login-it te suksesshem, klienti e ruan JWT token-in ne memorie lokale dhe shfaq keto komanda:

```text
request_data
logout
```

`request_data` kerkon te dhenat e mbrojtura nga serveri duke derguar JWT token-in si Bearer token.

`logout` e largon token-in nga klienti dhe e perfundon sesionin.

## Krijimi i `.pem` files

Projekti i krijon automatikisht `.pem` files kur startohet serveri:

```powershell
python server.py
```

Gjate startimit, serveri thirr funksionet `ensure_jwt_keys()` dhe `ensure_tls_certificate()` nga `jwt_utils.py`.

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
python -c "from jwt_utils import ensure_jwt_keys, ensure_tls_certificate; ensure_jwt_keys(); ensure_tls_certificate(); print('pem files created')"
```
