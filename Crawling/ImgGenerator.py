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
        # "model": "stable-diffusion-xl-v1-0",
        # "model": "realvis-xl-v4",
        "model": "reproduction-v3-31",
        "prompt": text,
        # 'negative_prompt' : 'text, letters, numbers, words, writing, font, sign, caption, watermark, logo, label, typography, typography, text overlay, bad composition, bad anatomy, disfigured, mutated body parts, bad hands, poorly drawn hands, extra limb, missing limb, floating limbs, disconnecting limbs, long neck, long body, undetailed skin, poorly drawn face, poorly rendered face, bad shadow, unrealistic, oversaturated, cartoon, abstract, amateur, grainy, blurry, messy, out of frame, out of focus, worst quality, low quality, ugly, watermark, censored, text font ui, whimiscal interpretation of the prompt, tiling, ugly arms, ugly hands, ugly feet, ugly eyes, ugly nose, ugly mouth, ugly teeth, ugly ears, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck)))',
        'negative_prompt' : 'bad composition, bad anatomy, disfigured, mutated body parts, bad hands, poorly drawn hands, extra limb, missing limb, floating limbs, disconnecting limbs, long neck, long body, undetailed skin, poorly drawn face, poorly rendered face, bad shadow, unrealistic, oversaturated, cartoon, abstract, amateur, grainy, blurry, messy, out of frame, out of focus, worst quality, low quality, ugly, watermark, censored, text font ui, whimiscal interpretation of the prompt, tiling, ugly arms, ugly hands, ugly feet, ugly eyes, ugly nose, ugly mouth, ugly teeth, ugly ears, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), NSFW, nude',
        "width": 768,
        "height": 1024,
        "steps": 20,
        "guidance": 7.5,
        "seed": 793407165,
        "scheduler": "euler",
        "output_format": "png",
        "response_format": "b64"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization" : "Bearer " + SECRET_KEY

    }

    print('img generator')
    response = requests.post(url, json=payload, headers=headers)
    print(response)

    return response
