from PIL import Image, ImageDraw
from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image
import torch

def generate_mask(image, start_x, start_y, end_x, end_y):
    img = load_image(image)
    width, height = img.size
    
    mask = Image.new("L", (width, height), 0)
    
    draw = ImageDraw.Draw(mask)
    draw.rectangle([start_x, start_y, end_x, end_y], fill=255)
    
    return mask

class Inpainting:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = AutoPipelineForInpainting.from_pretrained("diffusers/stable-diffusion-xl-1.0-inpainting-0.1", torch_dtype=torch.float16, variant="fp16").to(device)

        self.prompt = "complete the missing parts of the image"
        self.generator = torch.Generator(device="cuda").manual_seed(0)

    def __call__(self, image, mask_image):
        image = load_image(image)
        mask_image = load_image(mask_image)

        image = self.pipe(
            prompt=self.prompt,
            image=image,
            mask_image=mask_image,
            guidance_scale=8.0,
            num_inference_steps=20,
            strength=0.99,
            generator=self.generator,
            ).images[0]
        
        return image
