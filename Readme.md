########################## Service Layer #########################################

What is the Service Layer?

The simplest definition:

The Service Layer contains the application's business logic.

Your route should mainly answer:

"What HTTP request did I receive, and what HTTP response should I return?"

Your service should answer:

"What should the application actually do?"

Conceptually, your login endpoint is doing this:

POST /login
     │
     ▼
┌─────────────────────────┐
│       Route             │
│                         │
│ Get username            │
│        ↓                │
│ Query database          │
│        ↓                │
│ Check password          │
│        ↓                │
│ Create JWT              │
│        ↓                │
│ Return response         │
└─────────────────────────┘

It works.

There is nothing inherently wrong with it for a small application.

The problem appears when the application grows.

Imagine you later have:

POST /login
POST /mobile-login
POST /admin-login
POST /refresh-token

and perhaps another internal component needs to perform authentication.

If the actual authentication logic is sitting inside one HTTP route, you start duplicating logic.

3. What the Service Layer changes

We separate the responsibilities:

                 HTTP
                  │
                  ▼
           routes/auth.py
                  │
          "I received a
           login request"
                  │
                  ▼
          auth_service.py
                  │
          "Authenticate
             this user"
                  │
          ┌───────┴───────┐
          ▼               ▼
      Database        Password
                      verification
          │
          └───────┬───────┘
                  ▼
                 JWT

Now:

Route

Deals with:

HTTP request
HTTP response
HTTP status code
FastAPI-specific things

Service

Deals with:

Business logic
Database operations needed for the operation
Password verification
JWT creation
Business rules

Why not put everything in the route?

Suppose you have:

@router.post("/login")
def login(data: LoginRequest):

    user = database_lookup()

    if not user:
        ...

    if not verify_password():
        ...

    token = create_jwt()

    return token

The route now knows:

how the database works
how passwords are verified
how authentication works
how JWTs are generated
business rules

That's too much responsibility.

Instead:

@router.post("/login")
def login(data: LoginRequest):

    token = authenticate_user(
        data.username,
        data.password
    )

    return token

Much cleaner.

The route doesn't need to know how authentication happens.

Why not put everything in the route?

Suppose you have:

@router.post("/login")
def login(data: LoginRequest):

    user = database_lookup()

    if not user:
        ...

    if not verify_password():
        ...

    token = create_jwt()

    return token

The route now knows:

how the database works
how passwords are verified
how authentication works
how JWTs are generated
business rules

That's too much responsibility.

Instead:

@router.post("/login")
def login(data: LoginRequest):

    token = authenticate_user(
        data.username,
        data.password
    )

    return token

Much cleaner.

The route doesn't need to know how authentication happens.

Don't turn the Service Layer into another giant file.

For example, don't create:

services.py

with 2,000 lines.

Instead:

services/
├── auth_service.py
├── user_service.py
├── order_service.py
├── payment_service.py
└── ...

Each service represents a logical area of the application