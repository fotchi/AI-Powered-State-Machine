"""
Object Store pour les artefacts bruts (scripts générés, docs FLYNC,
futurs exports de diagrammes) -- le "Object/document store" du document
d'architecture.

Deux modes, choisis automatiquement :
- S3_BUCKET défini -> vrai stockage S3-compatible via boto3 (AWS S3 en
  prod, ou MinIO en local si S3_ENDPOINT_URL pointe dessus). Chiffrement
  au repos géré côté S3/MinIO (SSE) en prod -- pas le problème de ce module.
- Rien configuré -> fallback fichiers locaux sous backend/object_store/,
  chiffrés au repos avec Fernet (AES-128-CBC + HMAC) -- per Technical
  Design Document §9 "Data Protection... encryption... at rest for...
  the object store". Même interface -- donc le reste du code n'a pas à
  savoir lequel des deux est actif, ni que le fallback est chiffré.
"""
from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

ROOT = Path(__file__).resolve().parents[2]
LOCAL_STORE_ROOT = ROOT / "backend" / "object_store"

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")  # None = vrai AWS S3 ; sinon MinIO/compatible

# Fernet key for the local fallback's at-rest encryption. A fresh random key
# per restart would make every previously-written file permanently
# undecryptable, so (unlike JWT_SECRET, where that's a mild "please log in
# again") this one MUST persist: use the env var in production, otherwise
# generate it once into a local, gitignored key file and reuse it.
_KEY_FILE = ROOT / "backend" / ".object_store_key"


def _load_or_create_key() -> bytes:
    env_key = os.environ.get("OBJECT_STORE_ENCRYPTION_KEY")
    if env_key:
        return env_key.encode("utf-8")
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_bytes(key)
    print(f"[object_store] WARNING: OBJECT_STORE_ENCRYPTION_KEY not set -- generated a "
          f"local dev key at {_KEY_FILE}. Set the env var (and keep that file, or losing "
          f"it makes every locally-stored artifact unreadable) before deploying.")
    return key


_fernet = Fernet(_load_or_create_key())


def _use_s3() -> bool:
    return bool(S3_BUCKET)


_client = None


def _s3_client():
    global _client
    if _client is None:
        import boto3
        _client = boto3.client("s3", endpoint_url=S3_ENDPOINT_URL)
    return _client


def put_object(key: str, content: bytes | str, content_type: str = "text/plain") -> None:
    if isinstance(content, str):
        content = content.encode("utf-8")

    if _use_s3():
        _s3_client().put_object(Bucket=S3_BUCKET, Key=key, Body=content, ContentType=content_type)
        return

    path = LOCAL_STORE_ROOT / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_fernet.encrypt(content))


def get_object(key: str) -> bytes | None:
    if _use_s3():
        try:
            resp = _s3_client().get_object(Bucket=S3_BUCKET, Key=key)
            return resp["Body"].read()
        except _s3_client().exceptions.NoSuchKey:
            return None

    path = LOCAL_STORE_ROOT / key
    if not path.exists():
        return None
    raw = path.read_bytes()
    try:
        return _fernet.decrypt(raw)
    except InvalidToken:
        # Pre-existing plaintext file from before encryption was added.
        # Re-encrypt it on the way out so it's protected from here on.
        put_object(key, raw)
        return raw


def list_objects(prefix: str = "") -> list[str]:
    if _use_s3():
        paginator = _s3_client().get_paginator("list_objects_v2")
        keys = []
        for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
            keys.extend(obj["Key"] for obj in page.get("Contents", []))
        return keys

    if not LOCAL_STORE_ROOT.exists():
        return []
    return [
        str(p.relative_to(LOCAL_STORE_ROOT)).replace(os.sep, "/")
        for p in LOCAL_STORE_ROOT.rglob("*")
        if p.is_file() and str(p.relative_to(LOCAL_STORE_ROOT)).replace(os.sep, "/").startswith(prefix)
    ]


def delete_object(key: str) -> None:
    if _use_s3():
        _s3_client().delete_object(Bucket=S3_BUCKET, Key=key)
        return
    path = LOCAL_STORE_ROOT / key
    if path.exists():
        path.unlink()
