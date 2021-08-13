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
