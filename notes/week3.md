
## . Week 3 questions — answers

**1. Why does the server need `--host 0.0.0.0` inside the container, but the laptop publishes it with `-p 127.0.0.1:8000:8000`?**

Inside the container, `0.0.0.0` makes Uvicorn listen on all container network interfaces so Docker can reach it. The host-side `127.0.0.1` limits published access to the laptop itself, rather than exposing the port on every host interface.

**2. Which line rejected `{"owner":"admin"}`? What could happen if it were missing?**

`model_config = ConfigDict(extra="forbid")` in the Pydantic input model rejects fields that are not part of the allowed schema. Without strict validation, a real application might accept client-supplied fields that should only be controlled by the server, potentially enabling privilege or ownership manipulation if the application later trusts those fields.

**3. Why is `?limit=1000` a security problem, not only a performance problem?**

A very large response can consume server memory, CPU, database resources, and network bandwidth. An attacker could repeatedly request huge result sets to exhaust resources and deny service to legitimate users. A bounded limit reduces this abuse surface.

**4. Which user does `docker exec cv id` show, and why change it next week?**

The v1 image runs as `root` by default. Running an application as root increases the impact if the application is compromised; the next lab changes it to a dedicated non-root user.

**5. Give one reason to hide `/openapi.json` in production and one reason to publish it.**

A company may restrict it because it reveals API routes, schemas, and implementation details that help an attacker map the service. It may publish it for developer integrations, client generation, and easier API documentation. Hiding the schema is not a substitute for securing the endpoints.

**6. Why is `GET /deleteNote?id=3` a bad idea? Give two reasons.**

GET should be a safe method for reading data, not changing server state; automated crawlers, previews, caches, or browser prefetching may trigger GET requests unexpectedly. Also, state-changing actions should use an appropriate method such as DELETE and should have proper authorization and protections against cross-site request forgery where relevant.
