# s3_manager.py

import boto3
from flask import Blueprint, request, jsonify

s3_manager_bp = Blueprint('s3_manager', __name__)

# S3 클라이언트 생성
s3 = boto3.client('s3', aws_access_key_id='AKIASF7XT3HHBGPFORCM', aws_secret_access_key='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')

