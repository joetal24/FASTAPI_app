from redis.asyncio import Redis
from src.config import Config

JTI_EXPIRY = 3600  # 1 hour in seconds

token_blocklist = Redis(
    host=Config.REDIS_HOST, 
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True
)
async def add_jti_to_blocklist(jti: str)-> None:
    await token_blocklist.set(
        name = jti,
        value = "",
        ex = JTI_EXPIRY
    )
    
async def token_in_blocklist(jti:str) -> bool:
    token = await token_blocklist.get(name = jti)
    return token is not None