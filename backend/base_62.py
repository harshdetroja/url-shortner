BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    """Encodes an integer into a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    
    arr = []
    base = len(BASE62_ALPHABET)
    while num:
        num, rem = divmod(num, base)
        arr.append(BASE62_ALPHABET[rem])
    
    return "".join(reversed(arr))

def decode_base62(string: str) -> int:
    """Decodes a Base62 string back into an integer."""
    base = len(BASE62_ALPHABET)
    num = 0
    for char in string:
        num = num * base + BASE62_ALPHABET.index(char)
    return num
