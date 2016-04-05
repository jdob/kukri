#!/bin/bash

# User credentials must be sourced prior to running this
# (eventually I should merge this with the build script)

export IMAGE_NAME=${IMAGE_NAME:-"software-deployment-image"}
export IMAGE_PATH=${IMAGE_PATH:-"/tmp"}

glance image-create --name $IMAGE_NAME --disk-format qcow2 --container-format bare --file $IMAGE_PATH/$IMAGE_NAME.qcow2
