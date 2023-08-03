from fastapi import FastAPI
import uvicorn


from src.routes import contacts, auth,users
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from src.conf.config import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.authentification_router, prefix='/api')
app.include_router(users.user_router,prefix = '/api')
"""
define CORS
"""

origins = [ 
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
define limitations
"""
@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/")
def read_root():
  return {"message": "Welcome to Contact Book"}


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
