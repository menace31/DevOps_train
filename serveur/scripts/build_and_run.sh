#!/bin/bash
cd ..
sudo systemctl restart docker
docker compose up --build
