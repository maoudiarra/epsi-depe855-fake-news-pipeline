import os

print("=== Variables d'environnement contenant des accents ===")

for k, v in os.environ.items():
    try:
        v.encode("utf-8")
    except Exception:
        print(k, "=>", repr(v))

print("\n=== Variables PostgreSQL ===")

for k, v in os.environ.items():
    if "PG" in k.upper():
        print(k, "=", v)