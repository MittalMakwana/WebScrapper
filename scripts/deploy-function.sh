#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$(dirname $DIR)/src"


gcloud functions \
  deploy MainPage \
  --gen2 \
  --source=${SOURCE_DIR}/MainPage \
  --runtime=python311 \
  --trigger-http \
  --allow-unauthenticated \
  --env-vars-file ${SOURCE_DIR}/MainPage/.env.yaml \
  --entry-point=main \
  --region=us-west2 \
  --timeout=300 \