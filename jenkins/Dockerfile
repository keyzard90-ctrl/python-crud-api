# Image Jenkins untuk lab Windows (Docker Desktop / WSL2).
# Image resmi jenkins/jenkins tidak berisi python3 dan Docker CLI, dan binary
# docker.exe milik Windows tidak bisa di-mount ke container Linux.
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 curl \
 && rm -rf /var/lib/apt/lists/*
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
USER jenkins
