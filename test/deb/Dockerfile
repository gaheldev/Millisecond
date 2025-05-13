ARG distro=ubuntu:24.04
FROM ${distro}

RUN apt-get update -y

RUN apt-get install -y \
    libwayland-client0 \
    libwayland-cursor0 \
    libwayland-egl1 \
    wayland-protocols \
    dbus-x11 \
    sudo \
    curl \
    ca-certificates \
    && apt-get clean

RUN useradd -ms /bin/bash testuser

USER testuser
WORKDIR /home/testuser

# Copy the entrypoint script
COPY --chown=testuser:testuser entrypoint.sh /home/testuser/
RUN ["chmod", "+x", "/home/testuser/entrypoint.sh"]

ENTRYPOINT ["/home/testuser/entrypoint.sh"]
