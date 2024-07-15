import requests
import json
import base64
from PIL import Image
from io import BytesIO

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
SECRET_KEY = secrets['Img_API']

def SaveImg(response, path ='./image.png'):
    
    base64_string =response.json()['image']
    # Base64 문자열 디코딩
    image_data = base64.b64decode(base64_string)

    image = Image.open(BytesIO(image_data))

    image.save(path, "PNG")



def ImgGenerator(text):

    url = "https://api.getimg.ai/v1/stable-diffusion-xl/text-to-image"

    text +=', cartoon'
    payload = {
        "model": "stable-diffusion-xl-v1-0",
        "prompt": text,
        'negative_prompt' : 'text, letters, numbers, words, characters, typography, signs, captions, labels, text overlay',
        "width": 768,
        "height": 1024,
        "steps": 20,
        "guidance": 7.5,
        "seed": 42,
        "scheduler": "euler",
        "output_format": "png",
        "response_format": "b64"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization" : "Bearer " + SECRET_KEY

    }

    response = requests.post(url, json=payload, headers=headers)

    return response
