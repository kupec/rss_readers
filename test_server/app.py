import asyncio

from fastapi import FastAPI, Request, Response

app = FastAPI()

with open('sample.rss', 'r') as f:
    sample_rss = f.read()



@app.get('/')
async def status():
    return "OK"


@app.get('/sample.rss')
async def sample(delay: float = 0):
    await asyncio.sleep(delay)
    return Response(sample_rss)
