import openai
import os
from typing import Dict
import json
import logging
import re


OPENAI_BASE_URL = os.environ['OPENAI_BASE_URL']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
OPENAI_MODEL = os.environ['OPENAI_MODEL']



def pick_json_dict(content: str) -> Dict[str, str]:
    match = re.findall(r"```(.*?)```", content, re.DOTALL)[0]
    if match[:4] == 'json':
        match = match[4:]
    return json.loads(match)


class OpenaiHelper():
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=OPENAI_BASE_URL,
            api_key=OPENAI_API_KEY
            )
        self.novelai_prompt = """<目标>
根据用户输入跟要求给出和修改 novelai4 图片生成的提示词, 包括正向与反向, pixiv 的画师名有很强的加成, 如果有适合的画师风格必须添加画师名.
</目标>
<示例>
这是一些好的prompt, 请优先参考它的写法
prompt: 1girl, year 2024, official art, cover page, thin legs ::, -1.5::monocrome, flat color, simple background, text logo::, best quality, very aesthetic, solo, tareme, outdoors, photo background, sunlight, lens flare
negative_prompt: realistic, displeasing, very displeasing, normal quality, bad quality, blurry, lowres, upscaled, artistic error, film grain, scan artifacts, bad anatomy, bad hands, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, halftone, multiple views, logo, too many watermarks, @_@, mismatched pupils

prompt: 1other, eyecatch, headless, object head, flaming head, toned male, black suit, black necktie, white gloves, hatching (texture), chromatic aberration, outdoors, town, night, reaching towards viewer, perspective, blurry foreground, greyscale with colored background, blue fire, cowboy shot, fisheye, distortion, three quarter view, from below, location
negative_prompt: lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts, blurry, lowres, error
</示例>
<输出格式>
严格按照JSON格式, 不要输出任何多余字符, 也不要遗漏包裹json的反引号
```json
{
"prompt":"...",
"negative_prompt":"..."
}
```
</输出格式>"""

    def gen_novelai_prompt(self, prompt: str) -> Dict[str, str]:
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.novelai_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        content = response.choices[0].message.content
        logging.info("OpenAI response: %s", content)
        if not content: raise Exception("No content returned from OpenAI")
        return pick_json_dict(content)
