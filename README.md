This is a REST Web Api developed by Bryce Palmer using Python and the Flask microframework to be used for a budgeting application.

## Goals of this project:
1. Improve understanding of Python
2. Improve working knowledge of Web APIs and their interactions
3. Create a REST API that is capable of running an actual service
4. Learn the basics of Docker
5. Learn proper Web API security and standards

## API Endpoints

    1. APINAME/user/auth - generate an access token and refresh token <-- Coded  <-- Tests Created

    2. APINAME/user/categories & APINAME/user/categories/id - GET all/specific for the current user <-- Coded <-- Tests Created

    3. APINAME/user/categories/add - POST to add a new category for a user <-- Coded <-- Test Created

    4. APINAME/user/categories/id/update - POST to update a category for a user <-- Coded <-- Test Created

    5. APINAME/user/categories/id/expenses - GET to get all the expenses from a specific category <-- Coded <-- Test Created

    6. APINAME/user/categories/id/expenses/add  - POST to add a new expense for a category <-- Coded <-- Test Created

    7. APINAME/user - Accept GET and POST to get and modify information on a user <-- Coded <-- Tests Created
    
    8. APINAME/user/register - Registers a new user <-- Coded <-- Test Created

    9. APINAME/developer/register - Register a new developer that can leverage the API <-- Coded <-- Test Created

    10. APINAME/user/login - Login on behalf of a user <-- Coded <-- Test Created

    11. APINAME/user/categories/id/expenses/id/update <-- Coded <-- Test Created

    12. APINAME/cleanup_tests <-- Coded <-- Used at the end of the test file.

