async function generateKeyPair() {
    const keyPair = await window.crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
            hash: { name: "SHA-256" }
        },
        true,
        ["encrypt", "decrypt"]
    );

    // Экспорт публичного ключа
    const exportedPublic = await window.crypto.subtle.exportKey('spki', keyPair.publicKey);
    const publicKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(exportedPublic)));

    // Экспорт приватного ключа
    const exportedPrivate = await window.crypto.subtle.exportKey('pkcs8', keyPair.privateKey);const publicKeyPEM = `-----BEGIN PUBLIC KEY-----\n${publicKeyBase64}\n-----END PUBLIC KEY-----`;

    const privateKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(exportedPrivate)));

    return {
        publicKey: publicKeyBase64,
        privateKey: privateKeyBase64
    };
}

async function decryptDataRSA(privateKeyBase64, encryptedDataBase64) {
    // Импорт приватного ключа
    const privateKeyBinary = atob(privateKeyBase64);
    const privateKeyBuffer = new Uint8Array(privateKeyBinary.length);
    for (let i = 0; i < privateKeyBinary.length; i++) {
        privateKeyBuffer[i] = privateKeyBinary.charCodeAt(i);
    }

    const privateKey = await window.crypto.subtle.importKey(
        'pkcs8',
        privateKeyBuffer,
        {
            name: "RSA-OAEP",
            hash: { name: "SHA-256" }
        },
        true,
        ["decrypt"]
    );

    // Расшифровка данных
    const encryptedBinary = atob(encryptedDataBase64);
    const encryptedBuffer = new Uint8Array(encryptedBinary.length);
    for (let i = 0; i < encryptedBinary.length; i++) {
        encryptedBuffer[i] = encryptedBinary.charCodeAt(i);
    }

    const decrypted = await window.crypto.subtle.decrypt(
        { name: "RSA-OAEP" },
        privateKey,
        encryptedBuffer
    );

    return new TextDecoder().decode(decrypted);
}

async function encryptData(keyBase64, plainText) {
    // Конвертируем ключ из base64 в ArrayBuffer
    const keyBytes = new Uint8Array(atob(keyBase64).split('').map(c => c.charCodeAt(0)));

    // Импортируем ключ
    const key = await crypto.subtle.importKey(
        'raw',
        keyBytes,
        { name: 'AES-GCM' },
        false,
        ['encrypt']
    );

    // Генерируем случайный вектор инициализации (IV)
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // Шифруем данные
    const encoder = new TextEncoder();
    const data = encoder.encode(plainText);
    const encrypted = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv },
        key,
        data
    );

    // Объединяем IV и зашифрованные данные, конвертируем в base64
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encrypted), iv.length);

    return btoa(String.fromCharCode(...combined));
}

async function decryptData(keyBase64, encryptedText) {
    // Конвертируем ключ из base64 в ArrayBuffer
    const keyBytes = new Uint8Array(atob(keyBase64).split('').map(c => c.charCodeAt(0)));

    // Импортируем ключ
    const key = await crypto.subtle.importKey(
        'raw',
        keyBytes,
        { name: 'AES-GCM' },
        false,
        ['decrypt']
    );

    // Конвертируем зашифрованные данные из base64
    const encryptedBytes = new Uint8Array(atob(encryptedText).split('').map(c => c.charCodeAt(0)));

    // Извлекаем IV (первые 12 байт) и зашифрованные данные
    const iv = encryptedBytes.slice(0, 12);
    const data = encryptedBytes.slice(12);

    // Расшифровываем данные
    const decrypted = await crypto.subtle.decrypt(
        { name: 'AES-GCM', iv },
        key,
        data
    );

    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
}