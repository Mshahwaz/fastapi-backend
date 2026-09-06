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

We've progressively separated it into:

Project_Backend/
│
├── main.py
│
├── config.py
│
├── database.py
│
├── models.py
│
├── schemas.py
│
├── dependencies/
│   └── auth.py
│
├── routes/
│   ├── users.py
│   └── auth.py
│
├── services/
│   ├── auth_service.py
│   └── user_service.py
│
└── tests/
    └── test_main.py

And the request flow is now:

                         CLIENT
                            │
                            ▼
                       FastAPI
                            │
                            ▼
                    ┌──────────────┐
                    │    ROUTE     │
                    │              │
                    │ HTTP layer   │
                    └──────┬───────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
          DEPENDENCIES           SERVICE
                 │                   │
          Authentication        Business Logic
          Authorization               │
                 │                   │
                 └─────────┬─────────┘
                           ▼
                        MODEL
                           │
                           ▼
                       DATABASE
                           │
                           ▼
                      PostgreSQL

This is the point where I want you to understand something important:

This isn't about putting files into folders just to make the project look professional.

Each layer now has a specific responsibility.

Layer	Responsibility

routes/	HTTP endpoints
services/	Application/business logic
dependencies/	Reusable request dependencies
schemas.py	API input/output structures
models.py	Database entities
database.py	Database connection
config.py	Configuration
tests/	Verification

################## Dependencies and Backend Architecture ##########################

Step 1 — Client sends HTTP request

The client sends:

DELETE /users/15
Authorization: Bearer <JWT>

The important pieces are:

DELETE
   ↓
HTTP method

/users/15
   ↓
URL/path

Authorization: Bearer <JWT>
   ↓
HTTP header

You've already learned these concepts earlier.

3. Step 2 — FastAPI finds the route

FastAPI sees:

DELETE /users/15

and looks for a matching route:

@router.delete("/users/{user_id}")

It extracts:

user_id = 15

But before executing the actual route function, FastAPI looks at its dependencies.

That's where Depends() becomes important.

4. Step 3 — What is Depends()?

Suppose your route contains:

def delete_user_route(
    user_id: int,
    current_user: User = Depends(require_admin)
):

The important part is:

Depends(require_admin)

It means:

FastAPI, before executing this endpoint, execute require_admin() and give me its result.

You don't manually call:

require_admin()

FastAPI does it for you.

That's Dependency Injection.

What does "Dependency Injection" actually mean?

Ignore the complicated name for a moment.

Suppose your function needs:

current_user

Instead of your function figuring out how to obtain that user itself:

Route
 ├── extract token
 ├── decode JWT
 ├── find user
 └── check role

you say:

current_user = Depends(require_admin)

You're essentially telling FastAPI:

"I need a current authenticated admin user. You figure out how to provide one."

FastAPI then injects the result into:

current_user

Hence:

Dependency Injection = a dependency is supplied to your function by the framework.

6. Your dependency chain

Your application has:

require_admin()
      │
      ▼
get_current_user()

because your require_admin dependency depends on get_current_user.

Conceptually:

DELETE /users/15
        │
        ▼
 require_admin()
        │
        ▼
 get_current_user()
        │
        ▼
 HTTPBearer
        │
        ▼
 Authorization header
        │
        ▼
 Extract JWT
        │
        ▼
 Decode JWT
        │
        ▼
 Find User in DB
        │
        ▼
 current_user
        │
        ▼
 Check role == "admin"
        │
      ┌─┴─┐
     NO  YES
     │    │
    403   ▼
       route executes

This is one of the most useful things about FastAPI's dependency system.

7. Why don't we put authentication inside every route?

Imagine you had 50 protected endpoints.

Without dependencies:

GET /profile
   └── authentication code

PUT /profile
   └── authentication code

DELETE /profile
   └── authentication code

GET /orders
   └── authentication code

POST /orders
   └── authentication code

...

That's terrible duplication.

Instead:

              get_current_user()
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 /profile         /orders       /settings

All routes can reuse the same dependency.

Dependency vs Service

This is probably the most important distinction at this stage.

Consider:

current_user: User = Depends(require_admin)

versus:

delete_user(user_id)

They have completely different jobs.

Dependency

Answers:

"Can this request proceed, and what information does the route need?"

Example:

Is JWT valid?
Does user exist?
Is user admin?
Service

Answers:

"What does the application need to do?"

Example:

Find user
Delete user
Commit transaction

So:

                REQUEST
                   │
                   ▼
             DEPENDENCIES
                   │
           "Are you allowed?"
                   │
                  YES
                   ▼
                ROUTE
                   │
             "What endpoint?"
                   │
                   ▼
                SERVICE
                   │
             "Do the work"
                   │
                   ▼
               DATABASE
Why does the route still exist?

You might now wonder:

"If dependencies and services do everything, why do we even need routes?"

Because the route is the HTTP boundary.

For example:

@router.delete("/users/{user_id}")
def delete_user_route(...):
    return delete_user(user_id)

The route defines:

HTTP method
URL
request parameters
request schema
response schema
HTTP status code
dependencies

The service doesn't need to know that the operation came from:

DELETE /users/15

It just knows:

delete user 15

That makes the service independent of HTTP.

10. Model's job

Your models.py contains:

class User(SQLModel, table=True):

This represents the database entity.

Think:

User model
     │
     ▼
PostgreSQL table

The model answers:

"What does a User look like in the database?"

It doesn't answer:

"Should an HTTP request be allowed?"

and it doesn't answer:

"What should happen when someone registers?"

Those belong elsewhere.

11. Schema's job

Your schemas.py contains things like:

class User_create(...)
class UserResponse(...)
class UserUpdate(...)
class LoginRequest(...)

These describe API data.

For example:

POST /register

JSON
{
    "name": "John",
    "age": 25,
    "username": "john",
    "password": "secret"
}

User_create validates that incoming data.

Meanwhile:

UserResponse

controls what the API sends back.

So:

Schema
   ↓
API data

Model
   ↓
Database data

This distinction is extremely important.

12. Your complete architecture

At this point your application can be understood as:

                         CLIENT
                            │
                            ▼
                         ROUTES
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
          DEPENDENCIES                SCHEMAS
               │                         │
               │                         │
               ▼                         │
            SERVICES ◄───────────────────┘
               │
               ▼
             MODELS
               │
               ▼
            DATABASE
               │
               ▼
          PostgreSQL

And configuration supports everything:

config.py
    │
    ├── DATABASE_URL
    ├── SECRET_KEY
    ├── ALGORITHM
    └── token expiration

<--------------------Architecture Principle------------------>
ROUTE
"What HTTP operation is this?"

DEPENDENCY
"Is this request allowed / what does it depend on?"

SCHEMA
"What API data comes in/out?"

SERVICE
"What should the application do?"

MODEL
"What does the database entity look like?"

DATABASE
"How do I connect to persistence?"


<-- database session dependency---->
You currently have things conceptually like:

def get_all_users():

    with Session(engine) as session:
        users = session.exec(
            select(User)
        ).all()

        return users

and:

def get_user_by_id(user_id: int):

    with Session(engine) as session:
        user = session.get(User, user_id)
        ...

This works.

But notice:

Every service
    │
    ├── creates Session
    ├── performs operation
    └── closes Session

As the application grows, you may have:

20 services
   ↓
20 places managing database sessions

A cleaner pattern is to make the database session itself a dependency.

4. Create a database dependency

Your database.py currently contains your engine and table creation.

We'll add:

from sqlmodel import Session, SQLModel, create_engine

from config import DATABASE_URL

engine = create_engine(DATABASE_URL)


def create_db_and_table():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

The important new function is:

def get_session():
    with Session(engine) as session:
        yield session
What does yield do here?

Think of it as:

create session
     ↓
give session to whoever needs it
     ↓
route/service executes
     ↓
function finishes
     ↓
session closes

The with block guarantees cleanup.

5. Why yield instead of return?

This is an important Python concept.

With:

def get_session():
    with Session(engine) as session:
        return session

you're returning the object and leaving the with block.

The context manager then closes the session.

That's not what we want.

With:

def get_session():
    with Session(engine) as session:
        yield session

the dependency can provide the session while keeping the context alive.

Where should this dependency be used?

Here's where we need to make an architectural decision.

You might think:

def get_all_users(
    session: Session = Depends(get_session)
):

But don't do that in your service.

Why?

Because Depends() is a FastAPI mechanism.

We want the service layer to remain ordinary Python code.

Prefer:

FastAPI-specific
       │
       ▼
     Route
       │
       ▼
    Service

rather than making:

Service
  ↓
Depends()
  ↓
FastAPI

This keeps the service less coupled to FastAPI.

7. Better architecture

We can eventually have:

Route
 │
 ├── receives HTTP request
 │
 ├── FastAPI resolves Depends(get_session)
 │
 ▼
Service
 │
 ├── receives session
 │
 └── performs application logic

For example:

@router.get("/users")
def get_users(
    session: Session = Depends(get_session)
):
    return get_all_users(session)

And:

def get_all_users(session: Session):

    return session.exec(
        select(User)
    ).all()

Now the responsibilities are very clean.

Route
"I need a database session."
Dependency
"Here is a database session.
I'll clean it up afterward."
Service
"Given this session, retrieve all users."

Why inject the database session?

You've now done something that initially looks like unnecessary refactoring:

Route
  ↓
session = Depends(get_session)
  ↓
Service(session)
  ↓
Database

Why is this better?

The biggest reason is transaction control.

1. What is a transaction?

A transaction is a group of database operations treated as one logical unit.

Imagine an endpoint that needs to do:

Create Order
      ↓
Create Order Items
      ↓
Reduce Inventory
      ↓
Update Customer

Suppose this happens:

Create Order       ✅
Create Items       ✅
Reduce Inventory   ❌

You don't want the database left in this state:

Order exists
Items exist
Inventory NOT updated

You want either:

EVERYTHING succeeds

or:

EVERYTHING is rolled back

That's the fundamental purpose of a transaction.

2. Why does the session matter?

In SQLAlchemy/SQLModel, the Session is closely tied to transaction management.

For example:

session.add(order)
session.add(order_item)

session.commit()

Both changes can belong to the same transaction.

If something goes wrong before the commit:

session.rollback()

can undo the pending database changes.

So the session isn't merely:

"A connection to PostgreSQL."

It's also part of the unit-of-work / transaction context used by your application.

3. Why dependency injection helps

Suppose we have:

def create_order(session: Session):
    ...

and:

def create_order_item(session: Session):
    ...

The route can provide the same session:

              Session
                 │
        ┌────────┴────────┐
        ↓                 ↓
 create_order()   create_order_item()
        │                 │
        └────────┬────────┘
                 ↓
             COMMIT

Now both operations can participate in the same transaction.

Compare that with each service creating its own session:

create_order()
    ↓
Session A
    ↓
COMMIT

create_order_item()
    ↓
Session B
    ↓
COMMIT

Now they're separate transaction boundaries.

That's one of the major reasons we moved session creation out of the service.

4. Another important benefit: lifecycle

Your dependency:

def get_session():
    with Session(engine) as session:
        yield session

has a very useful lifecycle:

Request starts
     ↓
Create Session
     ↓
Inject Session
     ↓
Route executes
     ↓
Service executes
     ↓
Request finishes
     ↓
Session closes

The with statement guarantees cleanup.

You don't have to remember:

session.close()

inside every service.

5. yield is important here

This is worth understanding.

Your dependency is:

def get_session():
    with Session(engine) as session:
        yield session

Notice:

yield

rather than:

return

Conceptually:

                 get_session()
                      │
             ┌────────┴────────┐
             │                 │
          before             after
          yield              yield
             │                 │
       create session      cleanup
             │                 │
             ↓                 ↓
       route executes      close session

FastAPI can execute the dependency up to yield, provide the yielded value to your route, and then execute the cleanup portion afterward.

That's why this pattern is common for database sessions.