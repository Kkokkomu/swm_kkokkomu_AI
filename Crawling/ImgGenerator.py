import requests
import json
import base64
from PIL import Image
from io import BytesIO

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
SECRET_KEY = secrets['Img_API']


def ImgGenerator(text):

    url = "https://api.getimg.ai/v1/stable-diffusion-xl/text-to-image"

    text +=', cartoon'
    payload = {
        "model": "reproduction-v3-31",
        "prompt": text,
        'negative_prompt' : 'bad composition, bad anatomy, disfigured, mutated body parts, bad hands, poorly drawn hands, extra limb, missing limb, floating limbs, disconnecting limbs, long neck, long body, undetailed skin, poorly drawn face, poorly rendered face, bad shadow, unrealistic, oversaturated, abstract, amateur, grainy, blurry, messy, out of frame, out of focus, worst quality, low quality, ugly, watermark, censored, text font ui, whimiscal interpretation of the prompt, tiling, ugly arms, ugly hands, ugly feet, ugly eyes, ugly nose, ugly mouth, ugly teeth, ugly ears, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), NSFW, nude',
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
    response = response.json()['image']

    return response


def connectWebui(prompt):
# Define the URL and the payload to send.
    url = "http://10.0.4.18:7860"

    payload = {
        "prompt": "high quality, masterpiece, <lora:last-000008:0.7>, ",
        "negative_prompt":"""bad composition, bad anatomy, disfigured, Extra fingers, mutated body parts, poorly drawn hands,  bad hands, poorly drawn hands, extra limb, missing limb, floating limbs, disconnecting limbs, long neck, long body, 
        undetailed skin, poorly drawn face, poorly rendered face, bad shadow, unrealistic, oversaturated, cartoon, abstract, amateur, grainy, blurry, messy, out of frame, out of focus, worst quality, low quality, 
        ugly, watermark, censored, text font ui, whimiscal interpretation of the prompt, tiling, ugly arms, ugly hands, ugly feet, ugly eyes, ugly nose, ugly mouth, ugly teeth, ugly ears, bad anatomy, gross proportions, 
        malformed limbs, missing arms, missing legs, extra arms, extra legs, mutated hands, fused fingers, too many fingers, long neck, NSFW, nude, mutant, body horror""",
        "seed":394463348,
        "sampler_name":"DPM++ SDE",
        "scheduler":"Karras",
        "cfg_scale": 6.5,
        "width":512,
        "height":680,
        "denoising_strength":0.8,
        "batch_size":1,
        "steps": 20,
        "override_settings" : {
            "sd_model_checkpoint": "reproductionSDXL_2v12",

            "CLIP_stop_at_last_layers": 2,
        },

        "enable_hr": True,
        "hr_upscaler": "Latent",
        "hr_scale": 2,
        "script_name": "Prompts from file or textbox",
        "script_args":[
            False,
            False,
            "end",
            prompt, 
        
        ],
    }

    # Send said payload to said URL through the API.

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    result = []
    for i in range(3):
        result.append(r['images'][i])
        
    return result
