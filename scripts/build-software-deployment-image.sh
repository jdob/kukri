#!/bin/bash

# Builds an image with the necessary hooks to call back into Heat's
# software deployment functionality.

# Requires the following repositories (download and pip install into a venv):
# - https://git.openstack.org/openstack/diskimage-builder.git
# - https://git.OpenStack.org/OpenStack/tripleo-image-elements.git
# - https://git.openstack.org/openstack/heat-templates.git

# Variables likely to be changed by the caller
export OS=${OS:-"fedora"}   # fedora centos7, debian, opensuse, rhel, rhel7, or ubuntu
export IMAGE_NAME=${IMAGE_NAME:-"software-deployment-image"}
export IMAGE_PATH=${IMAGE_PATH:-"/tmp"}
export DEPLOYMENT_TOOLS=${DEPLOYMENT_TOOLS:-""}  # heat-config-cfn-init, heat-config-puppet, heat-config-salt

# Fairly standard stuff for software deployments
export ELEMENTS_PATH=tripleo-image-elements/elements:heat-templates/hot/software-config/elements
export BASE_ELEMENTS="$OS selinux-permissive"
export AGENT_ELEMENTS="os-collect-config os-refresh-config os-apply-config"
export DEPLOYMENT_BASE_ELEMENTS="heat-config heat-config-script"

# Summary
echo "------------------------------"
echo "Image Name:  $IMAGE_NAME"
echo "Destination: $IMAGE_PATH"
echo "OS:          $OS"
echo "------------------------------"

# Create the image
diskimage-builder/bin/disk-image-create vm $BASE_ELEMENTS $AGENT_ELEMENTS $DEPLOYMENT_BASE_ELEMENTS $DEPLOYMENT_TOOLS -o $IMAGE_PATH/$IMAGE_NAME
