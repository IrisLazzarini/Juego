"""
Utilidades de cifrado para el escape room de ciberseguridad.
"""

def caesar_shift(text: str, shift: int = -1) -> str:
    """
    Aplica el cifrado César a un texto.
    
    Args:
        text (str): Texto a cifrar/descifrar
        shift (int): Desplazamiento (negativo para descifrar, positivo para cifrar)
    
    Returns:
        str: Texto cifrado/descifrado
    """
    result = ""
    
    for char in text:
        if char.isalpha():
            # Determinar el código ASCII base (65 para mayúsculas, 97 para minúsculas)
            ascii_offset = 65 if char.isupper() else 97
            # Aplicar el desplazamiento y mantener en el rango 0-25
            shifted = (ord(char) - ascii_offset + shift) % 26
            # Convertir de vuelta a carácter
            result += chr(shifted + ascii_offset)
        else:
            # Mantener caracteres no alfabéticos sin cambios
            result += char
    
    return result


def encrypt_caesar(text: str, shift: int = 1) -> str:
    """
    Cifra un texto usando el cifrado César.
    
    Args:
        text (str): Texto a cifrar
        shift (int): Desplazamiento (por defecto 1)
    
    Returns:
        str: Texto cifrado
    """
    return caesar_shift(text, shift)


def decrypt_caesar(text: str, shift: int = 1) -> str:
    """
    Descifra un texto usando el cifrado César.
    
    Args:
        text (str): Texto a descifrar
        shift (int): Desplazamiento usado para cifrar (por defecto 1)
    
    Returns:
        str: Texto descifrado
    """
    return caesar_shift(text, -shift)


# Ejemplo de uso para testing
if __name__ == "__main__":
    # Test del cifrado César
    original = "There is no spoon"
    encrypted = encrypt_caesar(original, 1)
    decrypted = decrypt_caesar(encrypted, 1)
    
    print(f"Original: {original}")
    print(f"Cifrado:  {encrypted}")
    print(f"Descifrado: {decrypted}")
    print(f"¿Correcto?: {original == decrypted}")
