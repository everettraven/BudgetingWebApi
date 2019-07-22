This is a REST Web Api developed by Bryce Palmer using Python and the Flask microframework to be used for a budgeting application.

## Goals of this project:
1. Improve understanding of Python
2. Improve working knowledge of Web APIs and their interactions
3. Create a REST API to run an actual service
4. Learn the basics of Docker
5. Learn proper Web API security and standards
6. Learn new web and mobile technologies to use this API in a real world application

The following will describe the API url interactions, the format of json data to be sent by the request, and the json responses.

**APINAME/register**

JSON Request Body

Parameters : "username" (required), "password" (required. A specialized encryption key will be created to ensure that the user information is secured), "spendingLimit" (optional)
```
{
    "User":
    {
        "username": "Bryce.Palmer",
        "password": "This will be an encrypted value"
    }
}
```
With "spendingLimit"
```
{
    "User":
    {
        "username": "Bryce.Palmer",
        "password": "This will be an encrypted value",
        "spendingLimit": 3500
    }
}
```


**APINAME/auth**

This API endpoint will return a JWT to be used by the service using the API in order to authorize actions as a user. They will expire after a certain amount of time and will need to be refreshed.

Parameters: "username" (required), "password" (required. Will follow the same encryption as the register endpoint)

Example JSON Request
```
{
    "User":
    {
        "username": "Bryce.Palmer",
        "password": "This will be an encrypted value"
    }
}
```
Example JSON Response
```
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NjMwNDE0NzEsIm5iZiI6MTU2MzA0MTQ3MSwianRpIjoiOGU3Y2M2NTMtZjlkOC00MjE3LTk3ZDItNjQwNjljZjYzYTEyIiwiZXhwIjoxNTYzMDQxNTMxLCJpZGVudGl0eSI6MywiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.olCculLiDAbrkXbXY3o70ScXbRYAfhLMgaToPT5drR0",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NjMwNDE0NzEsIm5iZiI6MTU2MzA0MTQ3MSwianRpIjoiOGU3Y2M2NTMtZjlkOC00MjE3LTk3ZDItNjQwNjljZjYzYTEyIiwiZXhwIjoxNTYzMDQxNTMxLCJpZGVudGl0eSI6MywiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.olCculLiDAbrkXbXY3o70ScXbRYAfhLMgaToPT5drR0"
}
```


## Documentation & Code to work on:

    1. APINAME/auth/refresh

    2. APINAME/categories - GET all for a user

    3. APINAME/categories/add - POST to add for a user

    4. APINAME/expenses - GET all for a user

    5. APINAME/expenses/add  - POST to add for a user

    6. APINAME/expenses/update - POST to update for a user

    7. APINAME/categories/update - POST to update for a user

    8. APINAME/user - Accept GET and POST to get and modify information on a user

## Ideas for future API Endpoints:

OAuth2.0?
