#!/bin/sh

PYTHONPATH=../ locust -f ./locustfile.py --config ./locust.conf