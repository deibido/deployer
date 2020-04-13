# deployer
Simple tool to deploy a static website to AWS

## Prerequisites

You need to have [Docker installed](https://docs.docker.com/engine/install/)
Additionally you'll need python3.7 and virtualenv installed.
Also, you'll need an AWS account and API keys for your IAM user installed

## Limitations

This tool was developed and tested on Ubuntu so it will work on all Debian based
distros. Additionally, it doesn't use any Debian specific tools (e.g. apt) and is therefore
expected to work on most most *nix based distros.

However when deploying to EC2 it is using a hardcoded AMI which runs Ubuntu.
This shouldn't matter for developers but if anyone changes the AMI it may cause
problems.

This library assumes that any web project has all of its static files in a single
directory tree.

S3 deployments are hard-coded to deploy to the eu-west-1 region.

Because this tool assumes use of AWS free-tier, we're returning auto-generate
AWS DNS names. For a paid account with a managed domain in Route53, we'd
create an alias for S3 buckets (of course making sure that the buckets have
the correct domain suffix). And as for EC2 we'd set up a load balancer for the ASG 
with a route53 alias also.

## Usage

The first step is to copy your website into this directory using the provided script:

`./copy_to_local <PATH/TO/YOUR/WEB/PROJECT/>`

Make sure to have the trailing slash for your project path or else it will copy the root
directory too rather than just the files in it.

#### S3 deployment

If you'd like to deploy your website on S3 you can now run the following command:

`./deploy s3`

After which you be prompted to specify a mode of operation: Create, Update or Delete
and then you'll be asked for a bucket name.