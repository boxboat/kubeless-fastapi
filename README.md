# Kubeless FastAPI

This is a custom runtime for Kubeless that leverages FastAPI instead of Bottle.

## Function Definition

Using FastAPI means the function definition needs to be a little more rigid. BaseModel responses are required and a dataclass for params is also required. This ensures OpenAPI documentation is properly generated. 

Since FastAPI uses annotations for methods, the function must be prefixed with the method type (e.g., `get_`, `post_`, etc). 

In a GET request, the FastAPI request is directly passed in as the first func parameter. However, in other methods where a body is possible, the structure is this:

```
event:
  request: FastAPI request
  data: Data from request body
```

Below is a bare function definition that does nothing.

```python
from fastapi import Query, Header
from pydantic import BaseModel
from dataclasses import dataclass

# Function metadata for FastAPI
FUNCTION_NAME="myfunc"
FUNCTION_VERSION="1.0.0"
FUNCTION_SUMMARY="A basic function"
FUNCTION_RESPONSE_DESC="Some get response information"


# Required BaseModel for response
class GetResponse(BaseModel):
    pass

# Required dataclass for Params (query, header, path, cookie)
@dataclass
class Params:
    pass

# Handler with required method prefix.
def get_handler(event, context):

    return GetResponse()
```
    

## Example GET Request

GetResponse is a Pydantic BaseModel that d

```python
from fastapi import HTTPException, Query, Header
from pydantic import BaseModel
from dataclasses import dataclass

FUNCTION_NAME="mytest"
FUNCTION_VERSION="1.0.0"
FUNCTION_SUMMARY="A basic function"
FUNCTION_RESPONSE_DESC="Some get response information"


class GetResponse(BaseModel):
    details: dict

@dataclass
class Params:
    request_id: str = Header(None)
    my_param: str = Query(None)


def get_handler(event, context):
    try:
        data ={
            "request_id": event.headers["request-id"],
            "param": event.query_params["my_param"]
        }
    except Exception:
        raise HTTPException(status_code=400, detail="request id and my_param must be set")

    try:
        res = GetResponse(details=data)
    except Exception:
        raise HTTPException(status_code=500, detail="something went wrong")
    return res
```

## Example POST Request

```python
from fastapi import HTTPException, Header
from pydantic import BaseModel
from dataclasses import dataclass

FUNCTION_NAME="myfunc"
FUNCTION_VERSION="1.0.0"
FUNCTION_SUMMARY="A basic function"
FUNCTION_RESPONSE_DESC="Some post response inforation"


class PostRequest(BaseModel):
    name: str
    id: int

class PostResponse(BaseModel):
    name: str
    id: int
    request: str

@dataclass
class Params:
    request_id: str = Header(None)


def post_handler(event, context):
    try:
        kong_request_id = event.request.headers["request-id"]
    except Exception as e:
        raise HTTPException(status_code=400, detail="request id header required")

    try:
        res = PostResponse(name=event.data.name, id=event.data.id, request=request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"some error happened {e}")
    return res
```

## Request and Responses

### GET
```python
class GetResponse(BaseModel):
    pass

@dataclass
class Params:
    pass
```

### POST
```python
class PostRequest(BaseModel)
    pass


class PostResponse(BaseModel):
    pass


@dataclass
class Params:
    pass
```

### PUT
```python
class PutRequest(BaseModel):
    pass

class PutResponse(BaseModel):
    pass

@dataclass
class Params:
    pass

### DELETE
class DelRequest(BaseModel):
    pass

class DelResponse(BaseModel):
    pass

@dataclass
class Params:
    pass
```


## Use with Kubeless

To leverage this runtime, add the following to the `data.runtime-images` property in the Kubeless configmap:

```json
{
    "ID": "python-fastapi",
    "depName": "requirements.txt",
    "fileNameSuffix": ".py",
    "versions": [
        {
            "images": [
                {
                    "command": "pip install --prefix=$KUBELESS_INSTALL_VOLUME -r $KUBELESS_DEPS_FILE",
                    "image": "python:3.9",
                    "phase": "installation"
                },
                {
                    "env": {
                        "PYTHONPATH": "$(KUBELESS_INSTALL_VOLUME)/lib/python3.9/site-packages:$(KUBELESS_INSTALL_VOLUME)"
                    },
                    "image": "boxboat/kubeless-python-fastapi",
                    "phase": "runtime"
                }
            ],
            "name": "python-fastapi",
            "version": "3.9"
        }
    ]
}
```

Now you can run use the runtime name `kubeless function deploy --runtime python-fastapi3.9`
