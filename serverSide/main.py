from fastapi import FastAPI, Response, status, UploadFile, Form, File
from typing import Annotated
from sandbox import CodeRunner
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_socketio import SocketManager
from pm import ProcessManager
from process import Process
from config import Config
import asyncio

pm_running = ProcessManager()
pr_handlers = {}
cfg = Config()
code_runner = CodeRunner(cfg)

class CodeModel(BaseModel):
    code: str

class TestQueryModel(BaseModel):
    code: str
    filename: str

origins = ["*"]

app = FastAPI()
socket_manager = SocketManager(app=app, cors_allowed_origins='*')

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_methods=["POST","GET", "OPTIONS"],
    allow_headers=["*"]
)

def handle_bad_behavior(status_code, error: str, response: Response) -> bool:
    if status_code == -1:
        if "Server Error" in error:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return True
        else:
            response.status_code = 200
            return False

def wrap_response(error: str, is_server_failure: bool):
    if is_server_failure:
        return { "status": "failure", "message": error}

@app.post("/api/python/run")
async def run_code(code: CodeModel, response: Response):
    status_code, output, error, uuid = code_runner.run_code(code.code)
    output = code_runner.defend_from_bad_activity(output)
    if uuid:
        print("Process was created " + str(uuid))
        pm_running.processes[str(uuid)] = Process(code_runner.SOLUTIONS_DEFAULT_PATH + code_runner.FILE_DEFAULT_NAME, str(uuid))
        return {'status_code': code, 'output': output, 'error': error, 'uuid': uuid}
    if status_code == -1:
        state = handle_bad_behavior(status_code, error, response)
        wrap_response(error, state)
    return {'status_code': code, 'output': output, 'error': error}


async def process_timeout(pr: Process):
    await asyncio.sleep(cfg.input_process_timeout)
    if pm_running.processes.get(pr.uuid):
        pm_running.remove_process(pr.uuid)
        print(f"Process with uuid {pr.uuid} was removed because of timeout")
async def process_read(sid, pr: Process):
    while True:
        try:
            data = await pr.read_output()
            data = code_runner.defend_from_bad_activity(data)
            await socket_manager.emit("response", (data, pr.uuid), to=sid)
        except EOFError:
            pm_running.remove_process(pr.uuid)
            await socket_manager.emit("processend", (pr.uuid,))
            break
        except:
            break
            
@socket_manager.on
async def connect(sid, environ, auth):
    print(f"User with sid {sid} is connected")

@socket_manager.on
async def disconnect(sid):
    print(f"user with {sid} was disconnected")

@socket_manager.on("processconnect")
async def process_connect(sid, uuid: str):
    pr = pm_running.processes.get(str(uuid))
    if pr != None:
        task = asyncio.create_task(process_read(sid, pr))
        task2 = asyncio.create_task(process_timeout(pr))
        await task
        await task2
    else:
        await socket_manager.emit("resposne", "Process doesn't exist", uuid)
@socket_manager.on("prompt")
async def message(sid, uuid: str, data: str):
    print(sid, uuid, data)
    print(pm_running.processes.keys())
    print(data)
    pr = pm_running.processes.get(str(uuid))
    await pr.write_data(data)


@socket_manager.on("terminate")
async def terminate_process(sid, uuid: str):
    pm_running.processes.pop(str(uuid))