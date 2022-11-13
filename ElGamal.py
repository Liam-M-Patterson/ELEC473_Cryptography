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
		while pubKey.x == 0.0 or pubKey.y == 0.0 :
			self.privateKey =  self.gen_private_key()
			
			pubKey = self.curve.multiply(self.curve.g, self.privateKey)	
		return pubKey

	
	def encrypt(self, plaintext, public_key):

		print('encrypting')
		M = self.encode_point(plaintext)
		print('M:', M)
		return self.encrypt_point(M, public_key)



	def decrypt(self, private_key, ciphertext):

		M = self.decrypt_point(private_key, ciphertext)
		print('M ', M)
		decoded = self.decode_point(M)
		return decoded
	

	def encode_point(self, plaintext):
		print("ENCODE_POINT")
		plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
		print('plaintext :' , plaintext)
		x = int.from_bytes(plaintext, "big")
		
		y = self.curve.compute_y(x)
		
		while True:
			x = int.from_bytes(plaintext, "big")
			y = self.curve.compute_y(x)
			if y:
				return Point(x, y)
			plaintext += urandom(1)


	
	def decode_point(self, M):
		print("\n\nDECODE_POINT")
		print('decode point', M)
		print('type: ', type(M.x))

		x = int(M.x)
		print(x)
		byte_len = int_length_in_byte(x)
		print('byte len', byte_len)
		plaintext_len = (x >> ((byte_len - 1) * 8)) & 0xff
		print('plaintext len', plaintext_len)

		shift = byte_len - plaintext_len - 1
		print('shift', shift)

		plaintext = ((x >> ( shift * 8))
						& (int.from_bytes(b"\xff" * plaintext_len, "big")))
		print('plain', plaintext)
		return plaintext.to_bytes(plaintext_len, byteorder="big")
	
	
	def encrypt_point(self, plaintext, public_key):

		random.seed(urandom(1024))
		k = random.randint(1, self.curve.n)
		
		C1 = self.curve.multiply(self.curve.g, k)
		
		C2 = self.curve.add(plaintext, self.curve.multiply(public_key, k))

		return C1, C2

	def decrypt_point(self, private_key, ciphertext):
		print("DECRYPT")
		C1 = ciphertext[0]
		C2 = ciphertext[1]
		print(C1)
		print(C2)

		mul = self.curve.multiply(C1, (self.curve.n - private_key) )
		print('mul', mul)
		decrypted = self.curve.add(C2, mul)
		print('decrypted::', decrypted)
		return decrypted

if __name__ == "__main__":

	elg = ElGamal()