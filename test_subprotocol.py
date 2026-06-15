import asyncio, websockets, json, jwt
from datetime import datetime, timedelta, timezone

JWT_KEY = "62235bb1-5579-481d-9e00-c08b1d651edd"
token = jwt.encode(
    {"sub": "test", "email": "t@t.com",
     "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
    JWT_KEY, algorithm="HS256"
)

async def test():
    uri = "ws://nginx/ws/run"
    async with websockets.connect(uri, subprotocols=["bearer." + token], max_size=2**20, open_timeout=10) as ws:
        print("Connected via subprotocol!")
        code = "programa demo\ninicio\n  escreval 42;\nfim"
        await ws.send(json.dumps({"type": "compile_and_run", "code": code}))
        for _ in range(20):
            try:
                r = await asyncio.wait_for(ws.recv(), timeout=3)
                m = json.loads(r)
                t = m.get("type", "")
                if t == "stdout":
                    d = m.get("data", "")
                    print(f"STDOUT: {repr(d)}")
                elif t == "exit":
                    print(f"EXIT: code={m.get('code')}")
                    break
                elif t == "internal_error":
                    print(f"ERROR: {m.get('message')}")
                    break
                elif t in ("compile_error", "assemble_error", "link_error"):
                    print(f"COMPILE ERROR: {m.get('message') or m.get('stderr','')}")
                    break
                else:
                    print(f"EVENT: {t}")
            except asyncio.TimeoutError:
                print("TIMEOUT")
                break

asyncio.run(test())
