from os import urandom
from binascii import hexlify

INF_POINT = None
class EllipticCurve:

	def __init__(self):

		#secp160r1 parameters
		self.a = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFC
		self.b = 0x1C97BEFC54BD7A8B65ACF89F81D4D4ADC565FA45
		self.p = 2**160 - 2**31 - 1

		self.gx = 0x4A96B5688EF573284664698968C38BB913CBFC82
		self.gy = 0x23A628553168947D59DCC912042351377AC5FB32
		self.g = (self.gx, self.gy)
		
		self.n = 0x00000000000000000001F4C8F927AED3CA752257
		
	
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
	def multiply(self, g, scalar):

		if scalar == 0 or scalar > self.n:
			raise Exception("Invalid scalar")
		
		# convert to binary string
		scalarBin = str(bin(scalar))[2:]
		q = g

		for i in range(1, len(scalarBin)):
			q = self.double(q)

			if scalarBin[i] == "1":
				q = self.add(q, g)
		return q

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

	def generateKeyPair(self):

		pubKey = (0.0, 0.0)
		while pubKey == (0.0, 0.0):
			self.privateKey =  self.gen_private_key()
			
			pubKey = self.multiply(self.g, self.privateKey)
			print(pubKey)
		return pubKey

ec = EllipticCurve()

print('public key', ec.generateKeyPair())
print('private key', ec.privateKey)