from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os


# 1) Функция принимает публичный асимметричный ключ (в PEM формате) и шифрует им текстовые данные
def encrypt_with_public_key(public_key_pem: str, plaintext: str) -> str:
    """
    Шифрует текст публичным RSA ключом.
    """
    public_key_der = base64.b64decode(public_key_pem)

    # Загружаем из DER формата (вместо PEM)
    public_key = serialization.load_der_public_key(
        public_key_der,
        backend=default_backend()
    )

    # Шифруем текст
    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Возвращаем в base64 для удобства передачи
    return base64.b64encode(ciphertext).decode()


# 2) Функция генерирует симметричный ключ (AES-256)
def generate_symmetric_key() -> str:
    """
    Генерирует случайный симметричный ключ для AES-256.
    """
    # Генерируем 32 случайных байта (256 бит) для AES-256
    key = os.urandom(32)

    # Возвращаем в base64 для удобства хранения
    return base64.b64encode(key).decode()


# 3) Функция принимает симметричный ключ (base64) и текст, возвращает зашифрованные данные
def encrypt_with_symmetric_key(key_base64: str, plaintext: str) -> str:
    """
    Шифрует текст симметричным ключом AES-256-GCM.
    """
    # Декодируем ключ из base64
    key = base64.b64decode(key_base64)

    # Генерируем случайный nonce (12 байт для GCM)
    nonce = os.urandom(12)

    # Создаем шифр
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    )

    # Шифруем данные
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

    # Получаем тег аутентификации
    tag = encryptor.tag

    # Объединяем nonce, ciphertext и tag
    combined = nonce + ciphertext + tag

    # Возвращаем в base64
    return base64.b64encode(combined).decode()


# 4) Функция принимает симметричный ключ и зашифрованные данные, возвращает расшифрованные данные
def decrypt_with_symmetric_key(key_base64: str, ciphertext_base64: str) -> str:
    """
    Расшифровывает текст симметричным ключом AES-256-GCM.
    """
    # Декодируем ключ и данные из base64
    key = base64.b64decode(key_base64)
    combined = base64.b64decode(ciphertext_base64)

    # Разделяем на nonce, ciphertext и tag
    nonce = combined[:12]
    tag = combined[-16:]
    ciphertext = combined[12:-16]

    # Создаем шифр
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    )

    # Расшифровываем данные
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext.decode()