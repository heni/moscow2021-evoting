import binascii
import choices_pb2
import nacl.utils, nacl.public

def get_secret_object(private_key):
    return nacl.public.PrivateKey(binascii.a2b_hex(private_key))


def decode_choice(msg, nonce, pub_key, sKey):
    pKey = nacl.public.PublicKey(binascii.a2b_hex(pub_key))
    box = nacl.public.Box(sKey, pKey)
    pbData = box.decrypt(binascii.a2b_hex(msg), binascii.a2b_hex(nonce))
    offset = 2 + int.from_bytes(pbData[:2], 'big')
    return choices_pb2.Choices.FromString(pbData[offset:]).data
