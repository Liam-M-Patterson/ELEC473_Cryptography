from mod_sqrt import modsqrt
from typing import Optional
from dataclasses import dataclass
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
			self.n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
			# self.n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
		
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



if __name__ == "__main__":

	# ec = EllipticCurve('secp256k1')
	ec = EllipticCurve('small')

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