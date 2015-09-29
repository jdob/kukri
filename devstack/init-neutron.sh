#!/bin/bash

# Initializes a devstack Neutron installation to allow SSH and ping
# to created VMs.

PUB_NET=$(neutron net-list | grep public | awk '{print $2;}')
PRIV_NET=$(neutron net-list | grep private | awk '{print $2;}')
ROUTER_ID=$(neutron router-list | grep router1 | awk '{print $2;}')

neutron router-gateway-set $ROUTER_ID $PUB_NET

neutron security-group-rule-create --protocol icmp --direction ingress --remote-ip-prefix 0.0.0.0/0 default
neutron security-group-rule-create --protocol tcp --port-range-min 22 --port-range-max 22 --direction ingress default
