import dotenv
dotenv.load_dotenv(override=True)
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import StreamingResponse, Response
from novelai_adapter import novelai_api, Prompt2NovelaiArgs
import json
import traceback
from pydantic import BaseModel
from typing import Optional
from openai_adapter import OpenaiHelper
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
router = APIRouter(prefix="/novelai")


openai_helper = OpenaiHelper()


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: int):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            return {"error": "return sth for stop request"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Received request: {request.method} {request.url}")
    logging.info(f"Headers: {request.headers}")
    logging.info(f"Query params: {request.query_params}")
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        logging.info(f"Body: {body.decode('utf-8')}")
    response = await call_next(request)
    return response


@app.api_route("/ping")
async def pingpong():
    return "pong"


class SimpleNovelaiArgs(BaseModel):
    model: Optional[str] = ""
    prompt: str


@router.api_route("/", methods=["POST"])
@router.api_route("/images/generations", methods=["POST"])
async def novelai(body: SimpleNovelaiArgs):
    try:
        # add a function can auto gen prompt
        b64_image = None
        if body.prompt.startswith(">"):
            prompt_dict = openai_helper.gen_novelai_prompt(body.prompt)
            args = Prompt2NovelaiArgs(prompt=prompt_dict['prompt'], uc=prompt_dict['negative_prompt'])
            b64_image = await novelai_api.gen_b64_image(args)
        else:
            b64_image = await novelai_api.gen_b64_image(prompt=body.prompt)
        async def stream_response():
            yield json.dumps({
                "data": [
                    {
                        "b64_json": b64_image
                    }
                ]
            })
        return StreamingResponse(stream_response(), status_code=200, media_type="application/json")
    except Exception as e:
        traceback.print_exc()
        return {"error": "return sth for stop request"}


app.include_router(router)
app.add_middleware(TimeoutMiddleware, timeout=15)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
