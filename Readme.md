
For build and run using compose: 

`docker compose up --build`

show compose stack containers:

`docker compose ps`

show compose stack container logs:

`docker compose logs`

OR

`docker compose logs {service_name}`

To stop and remove compose stack (remove containers/network/anonymous volumes)

`docker compose down` 

To stop and remove containers and volumes (remove containers/network/anonymous volumes/named volumes)

`docker compose down -v`

To check health status of service

`docker inspect compose-backend-postgres --format="{{.State.Health.Status}}"`


Steps/Sequence to Run the Application :

1 : Setup/backup the test SQL in Postgres

` cat backup.sql | docker exec -i {postgres_container} psql -U {db_user} -d {db}`

2 : Run Database Migrations: Apply the latest Alembic migration scripts to update your PostgreSQL database schema to the latest version (head).

` alembic upgrade head `

3 : Start the FastAPI Server: Run Uvicorn to serve your FastAPI application