from EllipticCurve import EllipticCurve
from EllipticCurve import Point
from ElGamal import ElGamal

# plaintext = b"I am a Queen's University Student"
plaintext = b"Iamaasdasdasdklj"

elGamal = ElGamal()
public_key = elGamal.gen_key_pair()

print('pub: ', public_key)
ciphertext = elGamal.encrypt(plaintext, public_key)

print('cipher', ciphertext)

# orig = elGamal.decrypt(elGamal.privateKey, ciphertext)
# print('original', orig)

# print(elGamal.encode_point(plaintext))

print('\n\nstart of something new')
M = elGamal.encode_point(b'pleasework')
print('encoded plaintext', M)

cipher = elGamal.encrypt_point(M, public_key)
print('main- cipher', cipher)

decrypted = elGamal.decrypt_point(elGamal.privateKey, cipher)
orig = elGamal.decode_point(decrypted)
print('orig', orig)