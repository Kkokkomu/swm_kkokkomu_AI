import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import TotalBuild2S3

class ComponentRequest(BaseModel):
    id_list: list[int]
    count_news : int
    count_sports : int 
    count_entertain : int

## newsis일 경우 
    # id_list: list[int]
    # headline : int
    # politic : int
    # world : int
    # economy : int
    # IT : int
    # society : int
    # sports : int
    # entertain: int


    
app = FastAPI()

@app.post("/generate")
def test(request: ComponentRequest):
    print("generate ai resource")
    response = TotalBuild2S3.MakeSeperateComponent(request)

    ## RSS로 실행한 값
    # response = TotalBuild2S3.newsis_Make(request)

    return response




@app.get("/test")
def health_check():
    print("")
    return {"code": 200, "message": "success", "data": None}

# 메인 함수
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)