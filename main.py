from ElGamal import ElGamal

elGamal = ElGamal('secp256k1')
public_key = elGamal.gen_key_pair()
f = open("keys.txt", "w")
f.write('publicKey: ' + str( public_key ))
f.write('\nprivateKey: ' + str(elGamal.privateKey))
f.close()

cipher_file = open("ciphertext.txt", "w")
decrypted_file = open("decryped.txt", "w")
CHUNK_SIZE = 20

plaintexts = [b"I am an undergraduate student at queen\'s university.", b"Liam Matthew Cabral Patterson"]

for textNum, plaintext in enumerate(plaintexts):

    chunks = [plaintext[i:i+CHUNK_SIZE] for i in range(0, len(plaintext), CHUNK_SIZE)]

    ciphers = [elGamal.encrypt(chunk, public_key) for chunk in chunks]
    decryptions = [elGamal.decrypt(elGamal.privateKey, ciphertext) for ciphertext in ciphers]


    cipher_file.write(f"Ciphertext {textNum}: \n")
    for ciphertext in ciphers:
        cipher_file.write( "(" + str(ciphertext[0]) + " " + str(ciphertext[1]) +")\n\n")


    decrypted_file.write(f"Decrypted text {textNum}: \n")
    # print out each decrypted segment
    for decryption in decryptions:
        decrypted_file.write(str(decryption)[2:-1] +"\n")
        
    # print out the entire decryption joined together
    decrypted_plaintext = b"".join(decryptions)
    decrypted_file.write(str(decrypted_plaintext)[2:-1]+"\n\n")
    
    print(decrypted_plaintext == plaintext) 

    try:
        assert decrypted_plaintext == plaintext
    except AssertionError:
        print(f"The Decrypyted text '{decrypted_plaintext}' does not equal the plaintext '{plaintext}'")
        
    
cipher_file.close()
decrypted_file.close()