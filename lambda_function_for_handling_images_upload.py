import json
import base64
import boto3
import os
import uuid
import numpy as np
import cv2

std_folder = "standard_images/"
rs_folder = 'resized_images/'
s3 = boto3.client('s3')
bucket = "fit5225-gp40-photos"
width = 100

