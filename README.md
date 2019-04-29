# drone-portainer

Deploy and update Docker Swarm stacks via Portainer API

# Build

`docker build -t drone-portainer .`

# Usage

```
kind: pipeline
name: default

steps:
- name: deploy
  image: drone-portainer
  settings:
    url: https://portainer.example.org
    stack: example
    username:
      from_secret: portainer_username
    password:
      from_secret: portainer_password
    environment:
      VAR1: value
      VAR2: value
```

# Parameter Reference

`url`
URL of Portainer server

`stack`
Name of stack to create or update

`username`
Portainer username

`password`
Portainer password

`endpoint`
Endpoint name. Defaults to `primary`

`stackfile`
Stackfile path. Defaults to `docker-stack.yml`

`environment`
Environment variables
