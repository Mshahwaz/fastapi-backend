
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