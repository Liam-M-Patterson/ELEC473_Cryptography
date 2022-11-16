import random
from os import urandom
from EllipticCurve import EllipticCurve
from EllipticCurve import Point
from binascii import hexlify


def int_length_in_byte(n: int):
    assert n >= 0
    length = 0
    while n:
        n >>= 8
        length += 1
    return length


class ElGamal:
    def __init__(self, curve=None):

        self.curve = EllipticCurve(curve)
		
	# generates a random private key in order n
    def gen_private_key(self):
        order_bits = 0
        order = self.curve.n

        while order > 0:
            order >>= 1
            order_bits += 1

        order_bytes = (order_bits + 7) // 8
        extra_bits = order_bytes * 8 - order_bits

        rand = int(hexlify(urandom(order_bytes)), 16)
        rand >>= extra_bits

        while rand >= self.curve.n:
            rand = int(hexlify(urandom(order_bytes)), 16)
            rand >>= extra_bits

        return rand

    def gen_key_pair(self):

        pubKey = Point(0.0, 0.0)
        self.privateKey =  self.gen_private_key()
        
        pubKey = self.curve.multiply(self.curve.g, self.privateKey)	
        return pubKey


    def encrypt(self, plaintext: bytes, public_key: Point):

        M = self.encode_point(plaintext)
        return self.encrypt_point(M, public_key)


    def decrypt(self, private_key, ciphertext):

        M = self.decrypt_point(private_key, ciphertext)
        decoded = self.decode_point(M)
        return decoded


    def encode_point(self, plaintext: bytes):
        
        plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
        
        while True:
            x = int.from_bytes(plaintext, "big")
            y = self.curve.compute_y(x)
            if y:
                return Point(x, y)
            plaintext += urandom(1)

    def decode_point(self, M: Point) -> bytes:
        
        x = int(M.x)
        
        byte_len = int_length_in_byte(x)
        
        plaintext_len = (x >> ((byte_len - 1) * 8)) & 0xff
        
        shift = byte_len - plaintext_len - 1

        plaintext = ((x >> ( shift * 8)) & (int.from_bytes(b"\xff" * plaintext_len, "big")))
        
        return plaintext.to_bytes(plaintext_len, byteorder="big")


    def encrypt_point(self, plaintext: Point, public_key: Point):

        random.seed(urandom(1024))
        k = random.randint(1, self.curve.n)
        
        C1 = self.curve.multiply(self.curve.g, k)
        
        C2 = self.curve.add(plaintext, self.curve.multiply(public_key, k))

        return C1, C2

    def decrypt_point(self, private_key, ciphertext):
                
        mul = self.curve.multiply(ciphertext[0], (self.curve.n - private_key) )
        
        decrypted = self.curve.add(ciphertext[1], mul)
        
        return decrypted