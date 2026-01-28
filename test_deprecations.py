
try:
    import aifc
    print("aifc: OK")
except ImportError as e:
    print(f"aifc: ERROR - {e}")

try:
    import audioop
    print("audioop: OK")
except ImportError as e:
    print(f"audioop: ERROR - {e}")

try:
    import chunk
    print("chunk: OK")
except ImportError as e:
    print(f"chunk: ERROR - {e}")
