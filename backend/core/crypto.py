import binascii
from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError


class CryptoTools:
    @staticmethod
    def generate_pair():
        private_key = SigningKey.generate(curve=SECP256k1)
        public_key = private_key.get_verifying_key()
        return {
            "publicKey": binascii.hexlify(public_key.to_string()).decode('utf-8'),
            "privateKey": binascii.hexlify(private_key.to_string()).decode('utf-8')
        }

    @staticmethod
    def sign(message, private_key_hex):
        try:
            private_key = SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=SECP256k1)
            signature = private_key.sign(message.encode('utf-8'))
            return binascii.hexlify(signature).decode('utf-8')
        except (ValueError, binascii.Error):
            return "invalid signature"

    @staticmethod
    def verify_signature(message, signature_hex, public_key_hex):
        try:
            public_key = VerifyingKey.from_string(binascii.unhexlify(public_key_hex), curve=SECP256k1)
            signature = binascii.unhexlify(signature_hex)
            return public_key.verify(signature, message.encode('utf-8'))
        except (BadSignatureError, ValueError, binascii.Error):
            return False
