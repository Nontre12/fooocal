from abc import ABC, abstractmethod
import torch
from diffusers import FluxPipeline, StableDiffusionXLPipeline


class ImageGenerator(ABC):
    @abstractmethod
    def prompt(self, prompt: str, width: int, height: int, steps: int):
        pass

class BaseDiffusionGenerator(ImageGenerator):
    def __init__(self, model_class, model_name: str, torch_dtype):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        
        self.pipe = model_class.from_pretrained(
            model_name, torch_dtype=torch_dtype
        )
        self.pipe.enable_model_cpu_offload()

    def prompt(
        self,
        prompt: str,
        width: int = 832,
        height: int = 1216,
        steps: int = 20,
        guidance_scale: float = 7.0,
        seed: int = 0
    ):
        return self.pipe(
            prompt=prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=steps,
            generator=torch.Generator("cpu").manual_seed(seed),
        ).images[0]

class FLUX1DEVImageGenerator(BaseDiffusionGenerator):
    def __init__(self):
        super().__init__(FluxPipeline, "black-forest-labs/FLUX.1-dev", torch.bfloat16)

class JuggernautXLV9ImageGenerator(BaseDiffusionGenerator):
    def __init__(self):
        super().__init__(
            StableDiffusionXLPipeline, "RunDiffusion/Juggernaut-XL-v9", torch.float16
        )

class ImageGeneratorFactory:
    _generators = {
        "black-forest-labs/FLUX.1-dev": FLUX1DEVImageGenerator,
        "RunDiffusion/Juggernaut-XL-v9": JuggernautXLV9ImageGenerator,
    }

    @staticmethod
    def get_image_generator(model_name: str) -> ImageGenerator:
        generator_class = ImageGeneratorFactory._generators.get(model_name)
        if not generator_class:
            raise ValueError(f"Unsupported model: {model_name}")
        return generator_class()
