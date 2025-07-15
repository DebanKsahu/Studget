from typing import Any, Callable, Coroutine
from fastapi.routing import APIRoute
import jwt
from starlette.requests import Request
from starlette.responses import Response

from Utils.exceptions import Exceptions
from Utils.utility_functions import UtilsContainer


class DashboardRoute(APIRoute):

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_handler =  super().get_route_handler()

        async def custom_handler(request: Request) -> Response:
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise Exceptions.item_not_found_exception("Bearer Token")
            token = auth_header[len("Bearer "):]
            try:
                payload = UtilsContainer.jwt_utils.decode_jwt(token=token)
                student_id = payload.get("student_id")
                if student_id is None:
                    raise Exceptions.invalid_bearer_token_exception()
                
            except jwt.PyJWTError:
                raise Exceptions.unable_to_decode_token_exception()
            
            request.state.student_id = student_id

            return await original_handler(request)
        
        return custom_handler