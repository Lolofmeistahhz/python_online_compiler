import uvicorn


if __name__ == "__main__":
    # для поддержки https, wss
    # uvicorn.run("main:app", host="0.0.0.0", ssl_certfile="myserver.crt", ssl_keyfile="localhost.key")
    # для разработки 
    uvicorn.run("main:app", host="0.0.0.0")