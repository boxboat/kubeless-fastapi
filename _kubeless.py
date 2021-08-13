#!/usr/bin/env python

import importlib
import os
import sys
from pydantic import BaseModel
from fastapi import FastAPI, Request, Depends, Response
from starlette import status
import uvicorn
import prometheus_client as prom


# The reason this file has an underscore prefix in its name is to avoid a
# name collision with the user-defined module.
current_mod = os.path.basename(__file__).split('.')[0]
if os.getenv('MOD_NAME') == current_mod:
    raise ValueError(f'Module cannot be named {current_mod}')

sys.path.append('/kubeless')
mod = importlib.import_module(os.getenv('MOD_NAME'))
func = getattr(mod, os.getenv('FUNC_HANDLER'))
func_port = int(os.getenv('FUNC_PORT', 8080))
timeout = float(os.getenv('FUNC_TIMEOUT', 180))


app = FastAPI(version=mod.FUNCTION_VERSION, title=mod.FUNCTION_NAME)


function_context = {
    'function-name': mod,
    'timeout': timeout,
    'runtime': os.getenv('FUNC_RUNTIME'),
}

@app.middleware("http")
async def prom_metrics(request: Request, call_next):
    func_calls.labels(request.method).inc()
    func_calls.labels(request.url.path).inc()

    with func_hist.labels(request.method).time():
        with func_server_errors.labels(request.method).count_exceptions():
            response = await call_next(request)

            if response.status_code > 399:
                func_client_errors.labels(response.status_code).inc()
                
            return response



@app.get('/healthz')
async def healthz():
    return 'OK'


@app.get('/metrics')
async def metrics():

    return Response(content=prom.generate_latest(prom.REGISTRY), media_type=prom.CONTENT_TYPE_LATEST)


if str(func.__name__).startswith("get_"):
    if (not hasattr(mod, 'Params')) or (not hasattr(mod, 'GetResponse')):
        sys.exit("you must define a dataclass Params and a basemodel GetResponse")

    @app.get("/",
            status_code=status.HTTP_200_OK,
            response_model=mod.GetResponse,
            summary=mod.FUNCTION_SUMMARY,
            response_description=mod.FUNCTION_RESPONSE_DESC)
    async def handle_get_request(req: Request, params: mod.Params = Depends(mod.Params)):
        return func(req, function_context)
        
if str(func.__name__).startswith("post_"):
    if (not hasattr(mod, 'Params')) or (not hasattr(mod, 'PostResponse')) or (not hasattr(mod, 'PostRequest')):
        sys.exit("you must define a dataclass Params and the following basemodels: PostResponse, PostRequest")

    class PostRequest(BaseModel):
        data: mod.PostRequest
        request: Request

        class Config:
            arbitrary_types_allowed = True


    @app.post("/",
            status_code=status.HTTP_200_OK,
            response_model=mod.PostResponse,
            summary=mod.FUNCTION_SUMMARY,
            response_description=mod.FUNCTION_RESPONSE_DESC)
    async def handle_request(*, modreq: mod.PostRequest, request: Request, params: mod.Params = Depends(mod.Params)):
        req = PostRequest(data=modreq, request=request)

        return func(req, function_context)

if str(func.__name__).startswith("put_"):
    if (not hasattr(mod, 'Params')) or (not hasattr(mod, 'PutResponse')) or (not hasattr(mod, 'PutRequest')):
        sys.exit("you must define a dataclass Params and the following basemodels: PutResponse, PutRequest")

    class PutRequest(BaseModel):
        data: mod.PutRequest
        request: Request

        class Config:
            arbitrary_types_allowed = True


        @app.put("/",
                status_code=status.HTTP_200_OK,
                response_model=mod.PutResponse,
                summary=mod.FUNCTION_SUMMARY,
                response_description=mod.FUNCTION_RESPONSE_DESC)
        async def handle_request(*, modreq: mod.PutRequest, request: Request, params: mod.Params = Depends(mod.Params)):
            req = PutRequest(data=modreq, request=request)

            return func(req, function_context)

if str(func.__name__).startswith("delete_"):
    if (not hasattr(mod, 'Params')) or (not hasattr(mod, 'DelResponse')) or (not hasattr(mod, 'DelRequest')):
        sys.exit("you must define a dataclass Params and the following basemodels: DelResponse, DelRequest")

    class DelRequest(BaseModel):
        data: mod.DelRequest
        request: Request

        class Config:
            arbitrary_types_allowed = True


        @app.delete("/",
                status_code=status.HTTP_200_OK,
                response_model=mod.DelResponse,
                summary=mod.FUNCTION_SUMMARY,
                response_description=mod.FUNCTION_RESPONSE_DESC)
        async def handle_request(*, modreq: mod.DelRequest, request: Request, params: mod.Params = Depends(mod.Params)):
            req = DelRequest(data=modreq, request=request)

            return func(req, function_context)


if __name__ == '__main__':

    func_hist = prom.Histogram(
        'function_duration_seconds', 'Duration of user function in seconds', ['method']
    )
    func_calls = prom.Counter(
        'function_calls_total', 'Number of calls to user function', ['method']
    )
    func_server_errors = prom.Counter(
        'function_server_errors_total', 'Number of exceptions in user function', ['method']
    )
    func_client_errors = prom.Counter(
        'function_client_errors_total', 'Number of client error responses from user function', ['status_code']
    )


    uvicorn.run(app, port=func_port, host='0.0.0.0')
