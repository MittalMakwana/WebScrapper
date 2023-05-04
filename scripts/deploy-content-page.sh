#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$(dirname $DIR)/src"
FUNCTION_NAME="ContentPage"
TOPIC_ID="website"


gcloud functions \
  deploy ${FUNCTION_NAME} \
  --gen2 \
  --source=${SOURCE_DIR}/${FUNCTION_NAME} \
  --runtime=python311 \
  --trigger-topic=${TOPIC_ID}\
  --env-vars-file ${SOURCE_DIR}/${FUNCTION_NAME}/.env.yaml \
  --entry-point=main \
  --region=us-west2 \
  --timeout=300 \