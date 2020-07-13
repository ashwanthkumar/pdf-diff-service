#!/bin/bash

set -ex

docker build -t ashwanthkumar/pdf-diff-service:latest .
docker push ashwanthkumar/pdf-diff-service:latest
