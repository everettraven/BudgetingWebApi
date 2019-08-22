from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, verify_jwt_refresh_token_in_request


def OAuth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        access = False
        refresh = False
        code = None

        if request.json:
            data = request.json

            if "code" in data:
                code = data["code"]
            else:
                return jsonify(msg="An authorization code was not specified.")

        else:
            try:
                verify_jwt_in_request()
                access = True
            except:
                try:
                    verify_jwt_refresh_token_in_request()
                    refresh = True
                except:
                    return jsonify(msg="No valid tokens were given. Please ensure that a valid access or refresh token were given.")
            
        return fn(access, refresh, code, *args, **kwargs)
    
    return wrapper