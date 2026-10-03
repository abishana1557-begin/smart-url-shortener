# The master Base62 alphabet containing exactly 62 unique characters
BASE62_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def encode_id(id_num: int) -> str:
    """
    Takes a database integer ID (like 125) and converts it 
    into a short Base62 alphanumeric string (like 'cb').
    """
    if id_num == 0:
        return BASE62_ALPHABET[0]
        
    short_code = []
    
    # Mathematical loop: converts the number by repeatedly dividing by 62
    while id_num > 0:
        remainder = id_num % 62
        short_code.append(BASE62_ALPHABET[remainder])
        id_num = id_num // 62
        
    # Reverse the list because math remainders are calculated backwards
    return "".join(reversed(short_code))


# THIS PART IS FOR TESTING TONIGHT:
# Let's run a test right now to see the engine crunch numbers!
if __name__ == "__main__":
    test_id = 568392  # Imagine this is the 568,392nd link saved in your vault
    generated_code = encode_id(test_id)
    
    print("--- 🧠 Base62 Encoder Test ---")
    print(f"Original Database ID Number: {test_id}")
    print(f"Compressed Short URL Code:  {generated_code}")
