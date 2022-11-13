from EllipticCurve import EllipticCurve

plaintext = b"I am a Queen's University Student"

elGamal = EllipticCurve()
public_key = elGamal.gen_key_pair()

elGamal.encrypt(plaintext, public_key)


print(elGamal.encode_point(plaintext))