#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="${DIR}/../src"


gcloud functions \
  deploy MainPage \
  --source=${SOURCE_DIR}/MainPage \
  --runtime=python311 \
  --trigger-http \
  --allow-unauthenticated \
  --env-vars-file ${SOURCE_DIR}/MainPage/.env.yaml \
  --region=us-west2 \