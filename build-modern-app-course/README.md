# Building Modern Python Applications on AWS CDK Code

This folder stores the aws cdk python code of the infrastructure created during the [Building Modern Python Applications on AWS course](https://learning.edx.org/course/course-v1:AWS+OTP-AWSD12+1T2022a/home)

Currently, the code englobe at the lab 2 of module 2, which encompasses basic application on bucket, api gateway with mocked responses and aws cognito authentication.

To reproduce the infrastructure, follow the steps:

## Prepare application files

```bash
wget https://aws-tc-largeobjects.s3.amazonaws.com/DEV-AWS-MO-BuildingRedux/downloads/dragon_stats_one.txt
cp dragon_stats_one.txt <path>/course_files/
wget https://aws-tc-largeobjects.s3.amazonaws.com/DEV-AWS-MO-BuildingRedux/downloads/webapp3.zip
unzip webapp3.zip -d <path>/course_files/dragonsapp/
```

## Deploy stack

Pass a profile or use AWS credentials as enviroment variables

```bash
cdk deploy --context DragonAppPath=<path>/course_files/
```