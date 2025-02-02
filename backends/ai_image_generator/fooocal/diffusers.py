import torch
from diffusers import FluxPipeline, StableDiffusionXLPipeline

class FLUXImageGenerator:
    def __init__(self):
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16
        )
        self.pipe.enable_model_cpu_offload()

    def prompt(
        self,
        prompt: str,
        width: int = 832,
        height: int = 1216,
        steps: int = 20
    ):
        SEED = 0
        GUIDANCE_SCALE = 3.5

        out = self.pipe(
            prompt=prompt,
            guidance_scale=GUIDANCE_SCALE,
            height=height,
            width=width,
            num_inference_steps=steps,
            generator=torch.Generator("cpu").manual_seed(SEED),
        ).images[0]

        return out

class JuggernautXLV9ImageGenerator:
    def __init__(self):
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            "RunDiffusion/Juggernaut-XL-v9",
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        )
        self.pipe.enable_model_cpu_offload()

    def prompt(
        self,
        prompt: str,
        width: int = 832,
        height: int = 1216,
        steps: int = 20
    ):
        SEED = 0
        GUIDANCE_SCALE = 3.5

        out = self.pipe(
            prompt=prompt,
            guidance_scale=GUIDANCE_SCALE,
            height=height,
            width=width,
            num_inference_steps=steps,
            generator=torch.Generator("cpu").manual_seed(SEED),
        ).images[0]

        return out

class ImageGeneratorFactory:
    @staticmethod
    def get_image_generator(model_name: str):
        if model_name == "black-forest-labs/FLUX.1-dev":
            return FLUXImageGenerator()
        elif model_name == "RunDiffusion/Juggernaut-XL-v9":
            return JuggernautXLV9ImageGenerator()