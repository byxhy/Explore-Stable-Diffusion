# from stability_sdk.client import StabilityInference, process_artifacts_from_answers, open_images
import os
from tqdm import tqdm
from typing import List
from character_model import Line
import requests
import base64


def generate_image(prompt: str, prefix: str, width=1024, height=1024):

    STABILITY_KEY = 'sk-AwYTuVxAv24BbVD3qpe1W7E1LVvXJTTCjCm2N1zdLXidXxIR'

    body = {
        "samples": 1,
        "height": height,
        "width": width,
        "steps": 40,
        "cfg_scale": 5,
        "style_preset": "comic-book",
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
    }

    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {STABILITY_KEY}",
        },
        json=body,
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    # make sure the out directory exists
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")

    for i, image in enumerate(data["artifacts"]):
        with open(f'{prefix}.png', "wb") as f:
            f.write(base64.b64decode(image["base64"]))
