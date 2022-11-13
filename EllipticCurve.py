import random
from os import urandom
from binascii import hexlify
import codecs
from mod_sqrt import modsqrt

INF_POINT = None
class EllipticCurve:

	def __init__(self, curve=None):
		
		if curve == 'secp256k1':
			self.a = 0
			self.b = 7
			self.p = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1
			# self.p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
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
		else:
			#secp160r1 parameters
			self.a = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFC
			self.b = 0x1C97BEFC54BD7A8B65ACF89F81D4D4ADC565FA45
			self.p = 2**160 - 2**31 - 1

			self.gx = 0x4A96B5688EF573284664698968C38BB913CBFC82
			self.gy = 0x23A628553168947D59DCC912042351377AC5FB32
			
			self.n = 0x00000000000000000001F4C8F927AED3CA752257	

		self.g = (self.gx, self.gy)
	
	def modinv(self, a, n):
		lm, hm = 1, 0 
		low, high = a%n, n

		while low > 1:
			r = high/low

			nm = hm-lm*r
			temp = high-low*r

			lm, low, hm, high = nm, temp, lm, low
		return lm % n

	def add(self, x1, x2):

		num = (x2[1] - x1[1])
		denom = self.modinv(x2[0]-x1[0], self.p)
		lam =  (num*denom) % self.p

		x = (lam*lam-x1[0]-x2[0]) % self.p
		y = (lam*(x1[0]-x) -x1[1]) % self.p

		return (x,y)

	def double(self, x1):

		num = (3*x1[0]*x1[0] + self.a)

		denom = self.modinv(2*x1[1], self.p)
		lam =  (num*denom) % self.p

		x = (lam*lam- 2*x1[0]) % self.p
		y = (lam*(x1[0]-x) -x1[1]) % self.p

		return (x,y)

	# use the double and add algorithm to speed up the multiplication
	def multiply(self, point, scalar):

		# if scalar == 0 or scalar > self.n:
		# 	raise Exception("Invalid scalar")
		if scalar == 0:
			return INF_POINT
		
		# convert to binary string
		scalarBin = str(bin(scalar))[2:]
		q = point
		# print('multiply', scalarBin)
		# print('multiply point', point)
		for i in range(1, len(scalarBin)):
			q = self.double(q)

			if scalarBin[i] == "1":
				q = self.add(q, point)
		return q

	def compute_y(self, x):
		rhs = (x*x*x + self.a*x + self.b) % self.p
		print('rhs', rhs)
		y =  modsqrt(rhs, self.p)
		print('y', y)
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

		pubKey = (0.0, 0.0)
		while pubKey[0] == 0.0 or pubKey[1] == 0.0 :
			self.privateKey =  self.gen_private_key()
			
			pubKey = self.multiply(self.g, self.privateKey)	
		return pubKey

	
	def encrypt(self, plaintext, public_key):

		print('encrypting')
		M = self.encode_point(plaintext)
		print('M:', M)
		return self.encrypt_point(M, public_key)

		
	def encode_message(self, plaintext):

		encoded_text = plaintext.encode('utf-8')
		hex_text = encoded_text.hex()
		int_text = int(hex_text, 16)
		print('encoded:', int_text)
		return int_text


	def encode_point(self, plaintext):

		plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
		print('plaintext :' , plaintext)
		x = int.from_bytes(plaintext, "big")
		print(x)
		y = self.compute_y(x)
		
		# return (x,y)
		while True:
			x = int.from_bytes(plaintext, "big")
			y = self.compute_y(x)
			# print(y)
			if y:
				return(x, y)
			plaintext += urandom(1)

	def encrypt_point(self, plaintext, public_key):

		random.seed(urandom(1024))
		k = random.randint(1, self.n)

		C1 = self.multiply(self.g, k)
		C2 = self.add(plaintext, self.multiply(public_key, k))

		return C1, C2


	def decrypt(self, C):

		return


	def decode_message(self, encoded):
	
		hex_text = hex(encoded)[2:]
		print('hex_text', hex_text)
		
		decoded = codecs.decode(codecs.decode(hex_text,'hex'),'ascii')
		print('decoed: ', decoded)
		return decoded
	
	def decode_point(self, M):
		n = M
		byte_len = 0
		while n:
			n >>= 8
			byte_len += 1

		plaintext_len = (M.x >> ((byte_len - 1) * 8)) & 0xff
		plaintext = ((M.x >> ((byte_len - plaintext_len - 1) * 8))
						& (int.from_bytes(b"\xff" * plaintext_len, "big")))
		return plaintext.to_bytes(plaintext_len, byteorder="big")
	
	
	def decrypt_point(self, private_key, C1, C2):
		
		mul = self.multiply(C1, self.n - private_key)
		return self.add(C1, mul)






if __name__ == "__main__":

	plaintext = b"hi this is a message"

	# ec = EllipticCurve('secp256k1')
	ec = EllipticCurve()

	public_key = ec.gen_key_pair()
	print('public key', public_key)

	ec.encode_point(plaintext)

	# encrypted = ec.encrypt(plaintext, public_key)
	# encoded = ec.encode_message(plaintext)
	# ec.decode_message(encoded)


	