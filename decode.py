import binascii
import choices_pb2
import nacl.utils, nacl.public

PRIVATE_KEY = 0x54e3cf70f712b2ff727bde3849772fa811a9d5de796aa7d788d205aa86af04ad
SECRET_KEY_OBJ = nacl.public.PrivateKey(binascii.a2b_hex(hex(PRIVATE_KEY)[2:]))


def decode_choice(msg, nonce, pub_key, sKey=SECRET_KEY_OBJ):
    pKey = nacl.public.PublicKey(binascii.a2b_hex(pub_key))
    box = nacl.public.Box(sKey, pKey)
    pbData = box.decrypt(binascii.a2b_hex(msg), binascii.a2b_hex(nonce))
    offset = 2 + int.from_bytes(pbData[:2], 'big')
    return choices_pb2.Choices.FromString(pbData[offset:]).data
