# An efficient python3 program to find square root
# under modulo p when p is 7, 11, 19, 23, 31, ... etc.

# Utility function to do modular exponentiation.
# It returns (x^y) % p.
def powerMod(x, y, p) :

	res = 1 # Initialize result
	x %= p # Update x if it is more
			# than or equal to p

	while (y > 0):
		
		# If y is odd, multiply x with result
		if (y & 1):
			res = (res * x) % p
            
		# y must be even now
		y >>= 1 # y = y/2
		x = x **2 % p

	return res

# Assumption: p is of the
# form 3*i + 4 where i >= 1
def modsqrt(n, p):

	# Try "+(n^((p + 1)/4))"
	n %= p
	x = powerMod(n, (p + 1) // 4, p)
	if ( x ** 2 % p == n):
		return x

	# Try "-(n ^ ((p + 1)/4))"
	x = p - x
	if (x ** 2 % p == n):
		return x