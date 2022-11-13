import random
from os import urandom
from binascii import hexlify
import codecs
from mod_sqrt import modsqrt
from typing import Optional
from dataclasses import dataclass


def int_length_in_byte(n: int):
    assert n >= 0
    length = 0
    while n:
        n >>= 8
        length += 1
    return length

@dataclass
class Point:
	x: Optional[int]
	y: Optional[int]

	def is_at_infinity(self):
		return self.x is None and self.y is None

	def __eq__(self, rhs):
		return self.x == rhs.x and self.y == rhs.y 
	

INF_POINT = Point(None, None)

def modinv(a, n):
	a = a % n
	g, x, y = curve_gcd(a, n)

	return x % n 
		
def curve_gcd(a, b):
	if a == 0:
		return b, 0, 1
	else:
		g, y, x = curve_gcd(b % a, a)
		return g, x - (b//a) * y, y
class EllipticCurve:

	def __init__(self, curve=None):
		
		if curve == 'secp256k1':
			self.a = 0
			self.b = 7
			self.p = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1
			self.gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
			self.gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
			self.n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFBAAEDCE6AF48A03BBFD25E8CD0364141
		
		elif curve == 'secp224k1':
			self.a = 0x0
			self.b = 0x5
			self.p = 2**224 - 2**32 - 2**12 - 2**9 - 2**7 - 2**4 - 2 - 1
			self.gx = 0xA1455B334DF099DF30FC28A169A467E9E47075A90F7E650EB6B7A45C
			self.gy = 0x7E089FED7FBA344282CAFBD6F7E319F7C0B0BD59E2CA4BDB556D61A5
			self.n = 0x0001DCE8D2EC6184CAF0A971769FB1F7

		elif curve == 'small':
			self.a = 1
			self.b = 6
			self.p = 11
			self.gx = 2
			self.gy = 7
			self.n = 13
		else:
			#secp160r1 parameters
			self.a = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFC
			self.b = 0x1C97BEFC54BD7A8B65ACF89F81D4D4ADC565FA45
			self.p = 2**160 - 2**31 - 1
			self.gx = 0x4A96B5688EF573284664698968C38BB913CBFC82
			self.gy = 0x23A628553168947D59DCC912042351377AC5FB32
			self.n = 0x00000000000000000001F4C8F927AED3CA752257

			

		self.g = Point(self.gx, self.gy)

	def is_on_curve(self, p):

		lhs = p.y * p.y
		rhs = p.x*p.x*p.x + self.a*p.x + self.b

		return p.is_at_infinity() or ( (lhs-rhs) % self.p == 0 )
	
	


	def neg(self, p):
		return Point(p.x, -p.y % self.p)

	def add(self, p: Point, q: Point) -> Point:

		if p.is_at_infinity():
			return q
		if q.is_at_infinity():
			return p

		if p == self.neg(q):
			return INF_POINT
		
		if p == q:
			return self.double(p)
		
		_lambda = (q.y - p.y) * modinv( (q.x - p.x), self.p)
	
		x = (_lambda*_lambda - p.x - q.x) % self.p
		y = ((p.x - x) * _lambda - p.y) % self.p

		while x < 0:
			x += self.p
		while y < 0:
			y += self.p

		return Point(x, y)

	def double(self, p):
		
		_lambda = (3*p.x*p.x + self.a) * modinv(2*p.y, self.p)

		x = (_lambda*_lambda - 2*p.x) % self.p
		y = ((p.x - x) * _lambda - p.y) % self.p

		while x < 0:
			x += self.p
		while y < 0:
			y += self.p

		return Point(x, y)

	def multiply(self, point, scalar):

		temp = Point(point.x, point.y)

		scalarBin = bin(scalar)[2:]

		for i in range(1, len(scalarBin)):
			
			temp = self.double(temp)

			if scalarBin[i] == '1':
				temp = self.add(temp, point)

		return temp	


	def compute_y(self, x):
		rhs = (x*x*x + self.a*x + self.b) % self.p
		y =  modsqrt(rhs, self.p)
		return y

	# generates a random private key in order n
	def gen_private_key(self):
		order_bits = 0
		order = self.n

		while order > 0:
			order >>= 1
			order_bits += 1

		order_bytes = (order_bits + 7) // 8
		extra_bits = order_bytes * 8 - order_bits

		rand = int(hexlify(urandom(order_bytes)), 16)
		rand >>= extra_bits

		while rand >= self.n:
			rand = int(hexlify(urandom(order_bytes)), 16)
			rand >>= extra_bits

		return rand

	def gen_key_pair(self):

		pubKey = Point(0.0, 0.0)
		while pubKey.x == 0.0 or pubKey.y == 0.0 :
			self.privateKey =  self.gen_private_key()
			
			pubKey = self.multiply(self.g, self.privateKey)	
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
		
		y = self.compute_y(x)
		
		while True:
			x = int.from_bytes(plaintext, "big")
			y = self.compute_y(x)
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
		k = random.randint(1, self.n)
		
		C1 = self.multiply(self.g, k)
		
		C2 = self.add(plaintext, self.multiply(public_key, k))

		return C1, C2

	def decrypt_point(self, private_key, ciphertext):
		print("DECRYPT")
		C1 = ciphertext[0]
		C2 = ciphertext[1]
		print(C1)
		print(C2)

		mul = self.multiply(C1, (self.n - private_key) )
		print('mul', mul)
		decrypted = self.add(C2, mul)
		print('decrypted::', decrypted)
		return decrypted






if __name__ == "__main__":

	plaintext = b"hi this is a message"

	# ec = EllipticCurve('secp256k1')
	ec = EllipticCurve('small')
	# print(ec.g)

	public_key = ec.gen_key_pair()

	g = Point(2,7)

	print(g)

	print(ec.multiply(g, 2))
	print(ec.multiply(g, 3))
	print(ec.multiply(g, 4))
	print(ec.multiply(g, 5))
	print(ec.multiply(g, 6))
	print(ec.multiply(g, 7))
	print(ec.multiply(g, 8))
	print(ec.multiply(g, 9))
	print(ec.multiply(g, 10))
	print(ec.multiply(g, 11))
	print(ec.multiply(g, 12))
	print(ec.multiply(g, 13))
	print(ec.multiply(g, 14))

	# print(ec.add(ec.g, ec.g))
	# print(ec.double(ec.g))

	# print(ec.add(Point(5,2), Point(7,9)))

	print(modinv(3, ec.p))
	# ec.encode_point(plaintext)

	encrypted = ec.encrypt(plaintext, public_key)
	# encoded = ec.encode_message(plaintext)
	# ec.decode_message(encoded)


	