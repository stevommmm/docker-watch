## docker-watch

A events log for the web, using aiodocker and aiohttp. 

[Automated builds](https://hub.docker.com/r/c45y/docker-watch/)

## Usage
```
docker run -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock:ro c45y/docker-watch
```

![screenshot.png](screenshot.png)