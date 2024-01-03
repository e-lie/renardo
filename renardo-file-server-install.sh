#/bin/bash

## First create a container with:
# lxc launch ubuntu:22.04 renardo-file-server -c limits.cpu=2 -c limits.memory=4GiB -c security.nesting=true

## Then inside execute this script

set -eu

sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg openssh-server
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# add id_renardo_samples pubkey
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPxSdkMqUkvyQLEnf9UNb5BAtv27m5FzHl2yaVDTyBT0 root@renardo-samples' | sudo tee .ssh/authorized_keys

# need to replace Port 22 by another in sshd_config
# then balance -f 22887 & on the host to forward ssh traffic to lxc container

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

cat << EOF > docker-compose.yml
version: '3'
services:
    reverse-proxy:
        image: "traefik:v2.3"
        container_name: "traefik"
        command:
        #- "--log.level=DEBUG"
        - "--api.insecure=true"
        - "--providers.docker=true"
        - "--providers.docker.exposedbydefault=false"
        - "--entrypoints.websecure.address=:443"
        - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
        #- "--certificatesresolvers.myresolver.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
        - "--certificatesresolvers.myresolver.acme.email=eliegavoty@free.fr"
        - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
        ports:
        - "443:443"
        - "8080:8080"
        volumes:
        - "./letsencrypt:/letsencrypt"
        - "/var/run/docker.sock:/var/run/docker.sock:ro"

    renardo-samples-nginx:
        image: "nginx:1.25"
        #container_name: "simple-service"
        volumes:
        - "./default.conf:/etc/nginx/conf.d/default.conf:ro"
        - "./data:/usr/share/nginx/html:ro"
        labels:
        - "traefik.enable=true"
        - "traefik.http.routers.whoami.rule=Host(\`samples.renardo.org\`)"
        - "traefik.http.routers.whoami.entrypoints=websecure"
        - "traefik.http.routers.whoami.tls.certresolver=myresolver"
EOF

cat << EOF > default.conf
server {
    listen       80;
    listen  [::]:80;
    server_name  localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        sendfile           on;
        sendfile_max_chunk 1m;
        autoindex on;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
EOF

mkdir data

sudo docker compose up -d


