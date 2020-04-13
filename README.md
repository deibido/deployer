# deployer
Simple tool to deploy a static website to AWS

DO NOT USE THIS FOR PRODUCTION

## Prerequisites

Additionally you'll need python3.7 and virtualenv installed.
Also, you'll need an AWS account and API keys for your IAM user installed

This is enough for deploying to S3. To deploy to EC2 you need to 
have [Docker installed](https://docs.docker.com/engine/install/)

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

Create will generate a new hosting bucket, upload the static web resources and return
the public DNS of the bucket.

Update syncs the files in the local web directory (including deleting files in the remote
that no longer exist locally)

 Delete first deletes all the contents of the bucket and then deletes the bucket itself.
 
 #### EC2 deployment
 
 Firstly, you'll need to containerise your web app and push it to a remote docker registry.
 We provide a generic Dockerfile that will package your static files inside a container
 that has Nginx (web servcer) pre-installed.
 
 Run the following command:
 
 `./build_and_push <DOCKER_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>`
 
 As the name suggests, the script will build the Docker image and push it to your
 registry.
 
 To deploy it to AWS, run the following command:
 
 `./deploy ec2`
 
 Once again you'll be asked if you'd like to create, update or delete.
 
 Also, you'll be asked to provide a project name, the number of replicas you want,
 the Docker image to deploy and the vpc-id in which you want the web app launched.
 
 ```
Project Name: This will be used for the Cloudformation stack name and will need to be
used for subsequent changes to the stack (updates or deletes)
Replicas: Number of replicas of your web app. Will be divided equally among the number
of availability zones for HA
Docker image: Needs to be the same as the argument passed to the `build_and_push`
script (i.e. <DOCKER_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>
VPC ID: The VPC ID for which VPC the app will be deployed in (only needed for creation)
```

The create function will create a Cloudformation template using the parameters provided,
validate it and then deploy it. This will launch an autoscaling group which will use a launch
configuration to launch t2.micro instance across the configured AZs. The launch configuration
has custom user data that will install Docker onto the hosts and then pull and run the specified
Docker image.

The update function will allow the user to scale the number of replicas and update the Docker
image deployed to each host.

The delete function will tear down the cloudformation stack and all associated resources.

## Extra work

- Use load balancers and route53 for ASG to provide service discovery and HA
- Set up a VPC as illustrated in [this diagram](BasicNetworkImprovement.jpg). Having
the servers in private subnets will provide additional security as any attacker will need
to break into a public exposed endpoint in our network to continue the attack. Additionally
we can use TLS encrytion easily with our load balancers
- Use SSL everywhere
- Separate the cloud orchestration from the app deployment. Cloud infrastructure should be
relatively immutable compared to app development. It would be safer to separate the
infrastructure deployment from the app deployment
- Use real container orchestration (ECS, EKS etc.) instead of home rolled scripts