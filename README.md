# JWT-Authentication-Console-Application

## JWT
JWT (JSON Web Token) eshte nje standard qe perdoret per autentikim dhe shkembim te sigurt te informatave mes klientit dhe serverit. JWT ruan te dhenat ne forme 
tokeni

Kur nje perdorues ben login, klienti i dergon kredencialet te serveri. Serveri i kontrollon dhe nese jane te sakta krijon nje JWT token. Ky token i kthehet klientit dhe perdoret ne kerkesat e ardhshme per te vertetuar identitetin.

Avantazhi kryesor i JWT eshte qe perdoruesi nuk ka nevoje te dergoje passwordin ne cdo kerkese. Ne vend te tij perdoret tokeni, i cili permban informata te nevojshme dhe eshte i nenshkruar nga server.

JWT perbehet nga 3 pjese kryesore:

Header i cili permban informacion per tipin e tokenit dhe algoritmin e perdorur per nenshkrim.

Payload qe permban te dhena per perdoruesin, si username, roli ose kohezgjatja e tokenit.
Signature perdoret per te verifikuar qe tokeni nuk eshte ndryshuar dhe eshte krijuar nga serveri i autorizuar. 

Keto 3 pjese bashkohen dhe krijojne nje string unik qe perdoret si token.

Signature krijohet duke perdorur header, payload dhe nje secret key, te cilat kalojne brenda nje funksioni hash si RS256. Serveri krijon nje hash unik nga keto te dhena dhe e vendos ate si signature te tokenit. Kur klienti e dergon tokenin perseri, serveri i merr perseri header dhe payload, i kalon ne te njejtin funksion hash bashke me secret key dhe krijon nje hash te ri. Nese hash ri eshte i njejte me signature ekzistuese, tokeni konsiderohet valid.





## Pershkrimi i pjeseve te implementuara

### Serveri

`server.py` starton nje server qe pret lidhje ne `127.0.0.1:5050`. Serveri pranon kerkesa JSON nga klienti dhe i drejton ato sipas komandes:

- `login` kontrollon username/password dhe krijon JWT token nese kredencialet jane te sakta.
- `protected-data` kerkon Bearer token dhe kthen te dhena vetem nese JWT eshte valid.
- `logout` kthen pergjigje suksesi per mbylljen e sesionit nga klienti.

Serveri perdor TLS, trajton gabimet e JSON-it, gabimet e lidhjes dhe gabimet e papritura.

### Klienti

`client.py` eshte console application qe lejon perdoruesin te shkruaje username dhe password. Password-i nuk shfaqet ne console gjate shkrimit. Pas login-it te suksesshem, klienti e ruan JWT token-in ne memorie lokale dhe mund te ekzekutoje komandat:

- `request_data` kerkon te dhena te mbrojtura duke derguar JWT token si Bearer token.
- `logout` e largon token-in nga klienti dhe e perfundon sesionin.

### JWT

`jwt_utils.py` krijon dhe validon JWT token-at. Token-at nenshkruhen me algoritmin asimetrik `RS256`. Serveri perdor private key per nenshkrim, ndersa validimi behet me public key.

JWT permban:

- `sub` perdoruesin e autentikuar
- `iss` issuer-in e token-it
- `aud` audience-in
- `iat` kohen kur eshte leshuar token-i
- `exp` kohen kur token-i skadon

### Te dhenat e mbrojtura

Komanda `request_data` simulon qasjen ne nje endpoint te mbrojtur. Serveri kontrollon nese kerkesa ka Bearer token, nese token-i eshte valid dhe nese nuk ka skaduar. Nese token-i mungon, eshte i pavlefshem ose ka skaduar, serveri kthen `401 Unauthorized`.

## Setup

Krijo virtual environment:

```powershell
python -m venv .venv
```

Aktivizo virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalo paketat e nevojshme:

```powershell
pip install -r requirements.txt
```

Nese VS Code/Pylance nuk e njeh modulin `jwt`, zgjedh interpreter-in e projektit:

```text
Python: Select Interpreter -> .\.venv\Scripts\python.exe
```

## Ekzekutimi i programit

Starto serverin ne nje terminal:

```powershell
python server.py
```

Serveri duhet te shfaqe:

```text
Server: Waiting for connections on 127.0.0.1:5050...
```

Pastaj starto klientin ne nje terminal tjeter:

```powershell
python client.py
```

## User-at testues

```text
admin / admin123
sara / sara123
andi / andi123
rubeja / ruveja123
```

## Komandat e klientit

Pas login-it te suksesshem, klienti pranon keto komanda:

```text
request_data
logout
```

`request_data` kerkon te dhenat e mbrojtura nga serveri.

`logout` e largon token-in nga memoria e klientit dhe e perfundon sesionin.

## Shembull i ekzekutimit

### Server

```text
Server: Waiting for connections on 127.0.0.1:5050...
Connection established from ('127.0.0.1', 50001). Awaiting request...
Credentials received. Verifying...
Authentication successful. JWT issued.
Connection established from ('127.0.0.1', 50002). Awaiting request...
```

### Client

```text
Enter username: admin
Enter password: ********
Logged in. JWT token is:
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Token valid for user 'admin' until 2026-05-10T13:30:00+00:00.
Enter command ('request_data' or 'logout'): request_data
Accessing protected data...
Protected data received:
{
  "data": "This is protected data."
}
Enter command ('request_data' or 'logout'): logout
Logging out...
```

### Shembull me kredenciale te gabuara

```text
Enter username: admin
Enter password: *****
Unauthorized: invalid username or password
1. Try again
2. Quit
Choose option:
```

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

Nese deshiron me i kriju vetem keto files pa e lene serverin hapur, ekzekuto:

```powershell
python -c "from jwt_utils import ensure_jwt_keys, ensure_tls_certificate; ensure_jwt_keys(); ensure_tls_certificate(); print('pem files created')"
```

## Siguria dhe `.gitignore`

`.pem` files vendosen ne `.gitignore` sepse permbajne celesa privat/certifikata qe gjenerohen lokalisht dhe nuk duhet te ruhen apo shperndahen ne GitHub per arsye sigurie.

`.gitignore` gjithashtu perjashton folderin `.venv`, cache files dhe fajlla te tjere te panevojshem qe nuk duhet te jene pjese e repository.

## Testimi i shpejte

Mund te testohet logjika kryesore me:

```powershell
python -c "from server import route_request; r=route_request({'command':'login','username':'admin','password':'admin123'}); print(r['status']); print(route_request({'command':'protected-data','authorization':'Bearer '+r['token']})['status']); print(route_request({'command':'protected-data'})['status']); print(route_request({'command':'logout'})['status'])"
```

Rezultati i pritur:

```text
200
200
401
200
```
