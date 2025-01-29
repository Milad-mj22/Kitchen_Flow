from diffusers import StableDiffusionPipeline

# دانلود وزن Stable Diffusion
model = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-5")
model.save_pretrained("./path_to_save")
