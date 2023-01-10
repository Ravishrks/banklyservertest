"""Fastapi Server for Bankly"""

import random
import string
from base64 import b64encode


from fastapi import FastAPI
import aiohttp

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


app = FastAPI()

# Global values, Provided by ICICI
API_TEST_KEY = 'xUHvlTOtkLn37jnuG0Yp8zr2kivgRg6j'
# Company name to be passed in header
SRC_APP = 'Bankly'


@app.get("/")
def read_root():
    """# Access root"""
    return {"Hello": "Go to /send-payload route"}


@app.get("/send-payload/")
# send request to ICICI server
async def send_monthly_statement_api_request():
    """send request to Monthly Statement Service API"""

    async with aiohttp.ClientSession() as session:
        # Generate random string for request id
        requist_id = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(32))

        header = {'Content-Type': 'application/json',
                  "apikey": API_TEST_KEY, "SrcApp": SRC_APP}

        # Business Data to be send to ICICI server
        payload = "<xml><ReferenceNumber>20190704000084</ReferenceNumber><MerchantId>FLP0000001</MerchantId><MerchantPassword>admin12345</MerchantPassword><Product>VV01</Product><ProductCategory>1</ProductCategory><MobileNumber>9944838952</MobileNumber><TransactionRemark>FLIPKART Card Mobile Number link</TransactionRemark></xml>".encode("utf-8")

        # We have to encrypt key using ICICI's public key,
        # ICICI will use it's private key to decrypt key and use decrypted
        # key to decrypt encrypted data

        # key to be used to encrypt payload
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_CBC)
        ct_bytes = cipher_aes.encrypt(pad(payload, AES.block_size))
        iv = b64encode(cipher_aes.iv).decode('utf-8')

        # Reading RSA key from stored file
        recipient_key = RSA.import_key(open("ICICIUAT.cer").read())

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)  # Default is SHA1
        enc_session_key = cipher_rsa.encrypt(session_key)

        request_data = {
            "requestId": requist_id,  # Not mandatory
            "service": 'LOP',
            "encryptedKey": b64encode(enc_session_key).decode('utf-8'),
            "oaepHashingAlgorithm": 'SHA1',  # We are using MODE_CBC, as documented
            "iv": iv,
            "encryptedData": b64encode(cipher_aes.iv + ct_bytes).decode('utf-8'),
            "clientInfo": "",
            "optionalParam": ""
        }

        endpoint_url = 'https://apibankingonesandbox.icicibank.com/api/v1/pcms-chw?service=LinkedMobile'

        async with session.post(endpoint_url, headers=header, data=request_data) as response:
            #  decrypting response
            print(request_data)
            print("\n\n\n")

    return {"response_data": response.json, "header": response.headers, 'extra': response.text, "code": response.status, }
