from PIL import Image, ImageDraw
from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image
import torch

def generate_mask(image, start_x, start_y, end_x, end_y):
    img = Image.open(image)
    width, height = img.size
    
    mask = Image.new("L", (width, height), 0)
    
    draw = ImageDraw.Draw(mask)
    draw.rectangle([start_x, start_y, end_x, end_y], fill=255)
    
    return mask

class Inpainting:
    def __init__(self, device):
        self.device = device
        self.pipe = AutoPipelineForInpainting.from_pretrained("diffusers/stable-diffusion-xl-1.0-inpainting-0.1", torch_dtype=torch.float16, variant="fp16").to(device)

        self.prompt = "erase the text"
        self.generator = torch.Generator(device=device).manual_seed(0)

    def __call__(self, image, mask_image):
        image = Image.open(image)

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

if __name__ == "__main__":
    inpainting = Inpainting("mps")
    mask = generate_mask("image.jpg", 100, 100, 200, 200)
    inpainting("image.jpg", mask).save("output.jpg")