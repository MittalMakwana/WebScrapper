#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$(dirname $DIR)/src"
FUNCTION_NAME="MainPage"


gcloud functions \
  deploy ${FUNCTION_NAME} \
  --gen2 \
  --source=${SOURCE_DIR}/${FUNCTION_NAME} \
  --runtime=python311 \
  --trigger-http \
  --allow-unauthenticated \
  --env-vars-file ${SOURCE_DIR}/${FUNCTION_NAME}/.env.yaml \
  --entry-point=main \
  --region=us-west2 \
  --timeout=300 \