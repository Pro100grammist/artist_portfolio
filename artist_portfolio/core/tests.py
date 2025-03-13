# g = "Gothic"
# cs = "CS"
# d = "Dota"
#
# g_hash = hash(g)
# cs_hash = hash(cs)
# d_hash = hash(d)
#
# print("Hash")
# print(f"Gothic_hash: {g_hash}")
# print(f"CS_hash: {cs_hash}")
# print(f"Dota_hash: {d_hash}")
#
# # Маска для останніх 5 бітів
# mask = (2 ** 5) - 1  # 0b11111 = 31
#
# # Перетворення чисел у бінарний формат
# def to_bin(n):
#     """Перетворює число у бінарний рядок без префіксу '0b' і зберігає '-' для від'ємних чисел"""
#     return bin(n).replace("-0b", "-").replace("0b", "").zfill(64)  # Доповнюємо до 64 бітів
#
# g_binary = to_bin(g_hash)
# cs_binary = to_bin(cs_hash)
# d_binary = to_bin(d_hash)
# mask_binary = to_bin(mask)
#
# print("\nBinary Representation:")
# print(f"Gothic: {g_binary}")
# print(f"CS:     {cs_binary}")
# print(f"Dota:   {d_binary}")
# print(f"Mask:   {mask_binary}")
#
# # Побітове AND через цілі числа, але з виведенням у бінарному вигляді
# g_and = to_bin(g_hash & mask)
# cs_and = to_bin(cs_hash & mask)
# d_and = to_bin(d_hash & mask)
#
# print("\nBinary AND Result:")
# print(f"Gothic & Mask: {g_and} -> {g_hash & mask}")
# print(f"CS & Mask:     {cs_and} -> {cs_hash & mask}")
# print(f"Dota & Mask:   {d_and} -> {d_hash & mask}")


def custom_hash(s: str) -> int:
    """Improved custom hash function for strings."""
    hash_value = 0xcbf29ce484222325  # Initial "magic" number (FNV-1a)
    prime = 0x100000001b3  # A great simple number

    for char in s:
        hash_value ^= ord(char)  # XOR s code for the symbol
        hash_value *= prime  # Multiply on the great number
        hash_value ^= (hash_value >> 32)  # Shuffle lower and higher bits
        hash_value += 0x27d4eb2d  # Add a unique number for more variety
        hash_value &= 0xFFFFFFFFFFFFFFFF  # Limit to 64 bits

    return hash_value


# Testing our feature
words = ["Gothic", "CS", "Dota"]
hashes = {word: custom_hash(word) for word in words}

# Print hashes and their binary representations
print("Custom Hash Results:")
for word, h in hashes.items():
    print(f"{word}_hash: {h}")
    print(f"Binary: {bin(h)}")

# Mask (take 5 lowest bits)
mask = 0b11111

print("\nBinary AND Result:")
for word, h in hashes.items():
    print(f"{word} & Mask: {bin(h & mask)} -> {h & mask}")
