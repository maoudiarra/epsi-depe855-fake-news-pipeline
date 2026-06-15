import sys
import locale
import os

print("=" * 50)

print("Python :", sys.version)
print("Filesystem encoding :", sys.getfilesystemencoding())
print("Preferred encoding :", locale.getpreferredencoding())

print("\nVariables contenant PG :")

for k, v in os.environ.items():
    if "PG" in k.upper():
        print(f"{k} = {v}")

print("\nTerminé")