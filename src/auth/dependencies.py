from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, status, Depends
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService

user_service = UserService()


class AccessTokenBearer(HTTPBearer):
    
    def __init__(self,auto_error = True):
        super().__init__(auto_error = auto_error)
        
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        
        token = creds.credentials
        
        token_data = decode_token(token)
        
        if not self.token_valid:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )
        
        if token_data['refresh']:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail="Please provide access token"
            )
        
        return creds
    
        if await token_in_blocklist(token_data['jti']):
                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN,
                    detail={
                        "error":"Token has been revoked",
                        "resolution":"Please get a new token by logging in again"
                            
                            }
                    
                )
        
    def token_valid(self, token: str) -> bool:
        
        token_data = decode_token(token)
        
        if token_data is not None:
            return True
        
        else:
            return False
        
async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session)
    ):
    user_email = token_details['user']['email']
    
    user = await user_service.get_user_by_email(user_email, session)
    
    return user