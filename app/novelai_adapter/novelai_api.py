from novelai_api import NovelAIAPI
from novelai_api.ImagePreset import ImageModel, ImagePreset, ImageResolution, UCPreset
from pathlib import Path
from aiohttp import ClientSession
import os 
import io
import base64
from typing import Optional
from pydantic import BaseModel
import logging


NOVEL_AI_TOKEN = os.environ["NOVEL_AI_TOKEN"]


class Prompt2NovelaiArgs(BaseModel):
  prompt: str
  uc: str
  
  @classmethod
  def convert_from_promt(cls, prompt: str):
    if not prompt:
      raise Exception("Prompt must be provided")
    uc = "realistic, displeasing, very displeasing, normal quality, bad quality, blurry, lowres, upscaled, artistic error, film grain, scan artifacts, bad anatomy, bad hands, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, halftone, multiple views, logo, too many watermarks, @_@, mismatched pupils"
    try:
      prompt_parts = prompt.split("---")
      if len(prompt_parts) == 2:
        prompt = prompt_parts[0]
        uc = prompt_parts[1]
    except: pass
    return cls(prompt=prompt, uc=uc)
      

async def gen_b64_image(args: Optional[Prompt2NovelaiArgs] = None, prompt: Optional[str] = None, uc: Optional[str] = None):
  if not args:
    if not prompt:
      raise Exception("Either args or prompt must be provided")
    args = Prompt2NovelaiArgs.convert_from_promt(prompt)
  logging.info("Prompt2NovelAIArgs: %s", args)
  async with ClientSession(trust_env=True) as session:
    api = NovelAIAPI(session=session)
    await api.high_level.login_with_token(NOVEL_AI_TOKEN)
    model = ImageModel.Anime_v45_Full
    preset = ImagePreset.from_default_config(model)
    preset.resolution = ImageResolution.Normal_Landscape.value
    preset.steps = 28
    preset.uc = args.uc
    prompt = args.prompt
    async for _, img in api.high_level.generate_image(prompt, model, preset):
      base64_image = base64.b64encode(img).decode('utf-8')   # type: ignore
      return base64_image