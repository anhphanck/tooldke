
with open(r'd:\dke3\tooldke\custom_extract.py', 'rb') as f:
    header = f.read(32)
    print(f"File header (hex): {header.hex()}")
    print(f"File header (string): {header!r}")
