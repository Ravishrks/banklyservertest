import json
from typing import Union

from fastapi import FastAPI
import aiohttp

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/send-payload/")
async def send_xml_api_request():

    async with aiohttp.ClientSession() as session:
        api_key = 'xUHvlTOtkLn37jnuG0Yp8zr2kivgRg6j'
        header = {'Content-Type': 'application/xml',
                  "apikey": api_key, "SrcApp": ''}
        payload = b"""<xml>
                    <ReferenceNumber>20190704000084</ReferenceNumber>
                    <MerchantId>FLP0000001</MerchantId>
                    <MerchantPassword>admin12345</MerchantPassword>
                    <Product>VV01</Product>
                    <ProductCategory>1</ProductCategory>
                    <MobileNumber>9944838952</MobileNumber>
                    <TransactionRemark>FLIPKART Card Mobile Number
                    link</TransactionRemark>
                    </xml>"""

        # Encrypting data
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_ECB)
        ct_bytes = cipher.encrypt(pad(payload, AES.block_size))
        ct = b64encode(ct_bytes).decode('utf-8')

        data = {
            "requestId": "",
            "service": "LOP",
            "encryptedKey": key,
            "oaepHashingAlgorithm": "NONE",
            "iv": '',
            "encryptedData": ct,
            "clientInfo": "",
            "optionalParam": ""


        }

        endpoint_url = 'https://apibankingonesandbox.icicibank.com/api/v1/pcms-chw?service=LinkedMobile'

        async with session.post(endpoint_url, headers=header, data=data) as response:
            #  decrypting response
            pass

            # try:
            #     b64 = json.loads(response)
            #     iv = b64decode(b64['iv'])

            #     # removeFirst16Bytes(Base64Decode(encryptedData)
            #     ct = b64decode(b64['encryptedData'])
            #     cipher = AES.new(key, AES.MODE_ECB, iv)
            #     pt = unpad(cipher.decrypt(ct), AES.block_size)
            #     print("The message was: ", pt)
            # except (ValueError, KeyError):
            #     print("Incorrect decryption")

    return {"data": response.json,"1":response.headers }
