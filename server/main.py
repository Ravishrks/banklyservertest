# Fastapi server

import random
import string

from fastapi import FastAPI
import aiohttp

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from base64 import b64encode


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "Go to /send-payload route"}


@app.get("/send-payload/")
# send request to ICICI server
async def send_link_mobile_api_request():

    async with aiohttp.ClientSession() as session:

        # Company name to be passed in header
        src_app = 'Bankly'
        # Generate random string for request id
        requist_id = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(32))
        # Provided by ICICI
        api_key = 'xUHvlTOtkLn37jnuG0Yp8zr2kivgRg6j'
        # We are using MODE_CBC, so opanHashAlgorithm value is 'SHA1'.
        open_hash_algorithm = 'SHA1'

        # Service, using 'LinkedMobile for testing"
        service = 'LinkedMobile'

        header = {'Content-Type': 'application/json',
                  "apikey": api_key, "SrcApp": src_app}
        # Business Data to be send to ICICI server

        payload = ''.encode("utf-8")

        # We have to encrypt key using ICICI's public key,
        # ICICI will use it's private key to decrypt key and use decrypted
        # key to decrypt encrypted data

        # key to be used to encrypt payload
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_CBC)
        ct_bytes = cipher_aes.encrypt(pad(payload, AES.block_size))
        iv = b64encode(cipher_aes.iv).decode('utf-8')

        # encrypted data
        cypher_text = b64encode(ct_bytes).decode('utf-8')

        # Reading RSA key from stored file
        rsa_key_file = open('../rsa_key/ICICIUAT.cer', 'r')
        recipient_key = RSA.import_key(rsa_key_file.read())

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        data = {
            "requestId": requist_id,
            "service": service,
            "encryptedKey": enc_session_key,
            "oaepHashingAlgorithm": open_hash_algorithm,
            "iv": iv,
            "encryptedData": cypher_text,
        }

        endpoint_url = 'https://apibankingonesandbox.icicibank.com/api/v1/pcms-chw?service=LinkedMobile'

        async with session.post(endpoint_url, headers=header, data=data) as response:
            #  decrypting response
            pass

    return {"data": response.json, "header": response.headers, 'extra': response.text, "code": response.status}
