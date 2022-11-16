from EllipticCurve import EllipticCurve
from EllipticCurve import Point
from ElGamal import ElGamal

plaintext = b"I am an undergraduate student at queen\'s university."

n = 20
chunks = [plaintext[i:i+n] for i in range(0, len(plaintext), n)]
elGamal = ElGamal('secp256k1')
public_key = elGamal.gen_key_pair()

f = open("keys.txt", "w")
f.write('publicKey: ' + str(public_key))
f.write('\nprivateKey: ' + str(elGamal.privateKey))
f.close()

ciphers = [elGamal.encrypt(chunk, public_key) for chunk in chunks]

f = open("ciphertext.txt", "w")
for ciphertext in ciphers:
    f.write( "(" + str(ciphertext[0]) + " " + str(ciphertext[1]) +")\n")
f.close()

decryptions = [elGamal.decrypt(elGamal.privateKey, ciphertext) for ciphertext in ciphers]

f = open("decryped.txt", "w")
for decryption in decryptions:
    f.write(str(decryption)[2:-1] +"\n")

decrypted_plaintext = b"".join(decryptions)
f.write(str(decrypted_plaintext)[2:-1])
f.close()


print(decrypted_plaintext == plaintext)