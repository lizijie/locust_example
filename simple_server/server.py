import asyncio
import websockets
import random

from common.sproto_utils import load_protos, sproto_encode, sproto_decode
load_protos("../proto")

async def handler_server_list(websocket):
    try:
        async for bytes in websocket:
            name, _ = sproto_decode(bytes)
            print(f"rec {name}")
            if name == "ServerListRequest":
                await websocket.send(sproto_encode(
                    "ServerListResponse", 
                    {
                        "ServerList":["localhost:8766"]
                    })
                )
    except websockets.ConnectionClosed:
        print("handler_server_list: Client disconnected")

async def handler_login(websocket):
    try:
        async for bytes in websocket:
            name, pkg = sproto_decode(bytes)
            print(f"rec {name}")
            if name == "LoginReuest":
                await websocket.send(sproto_encode(
                    "LoginRespone", 
                    {
                        "MyValue": random.randint(1, 100)
                    })
                )
            elif name == "EchoRequest":
                text = pkg["Text"]
                await websocket.send(sproto_encode(
                    "EchoResponse", 
                    {
                        "Text": f"{text} from server"
                    })
                )
    except websockets.ConnectionClosed:
        print("handler_login: Client disconnected")

async def main():
    server_one = websockets.serve(handler_server_list, "localhost", 8765)  # 监听端口 8765
    server_two = websockets.serve(handler_login, "localhost", 8766)  # 监听端口 8766

    print("Starting two WebSocket servers...")
    async with server_one, server_two:
        await asyncio.Future()  # 阻塞运行，保持服务器持续运行

if __name__ == "__main__":
    asyncio.run(main())
