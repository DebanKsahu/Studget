from fastapi import status, HTTPException

class Exceptions:

    @staticmethod
    def item_not_found_exception(item_name: str):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[
                {
                    "loc": ["path", item_name],
                    "msg": f"{item_name} not found",
                    "type": "not_found"
                }
            ]
        )

    @staticmethod
    def wrong_authentication_exception(reason: str = "Wrong authentication credentials"):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "loc": ["auth"],
                    "msg": reason,
                    "type": "authentication_error"
                }
            ]
        )

    @staticmethod
    def item_already_exists_exception(item_name: str):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[
                {
                    "loc": ["body", item_name],
                    "msg": f"{item_name} already exists",
                    "type": "already_exists"
                }
            ]
        )

    @staticmethod
    def empty_input_exception(field_name: str = "Input"):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": ["body", field_name],
                    "msg": f"{field_name} must not be empty",
                    "type": "value_error"
                }
            ]
        )

    @staticmethod
    def invalid_input_type_exception(field_name: str = "Input", expected_type: str = "valid type"):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": ["body", field_name],
                    "msg": f"{field_name} must be of type {expected_type}",
                    "type": "type_error"
                }
            ]
        )

    @staticmethod
    def invalid_bearer_token_exception(reason: str = "Invalid or missing bearer token"):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "loc": ["header", "Authorization"],
                    "msg": reason,
                    "type": "invalid_bearer_token"
                }
            ]
        )

    @staticmethod
    def unable_to_decode_token_exception(reason: str = "Unable to decode token"):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "loc": ["header", "Authorization"],
                    "msg": reason,
                    "type": "unable_to_decode_token"
                }
            ]
        )