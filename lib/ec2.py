import os
from typing import List
from dataclasses import dataclass

import boto3

from troposphere import autoscaling, Base64, Join, Parameter, Ref, Template


@dataclass()
class VpcDetails:
    security_group: str
    subnet_ids: List[str]


def default_data(vpc_id: str) -> VpcDetails:
    cli = boto3.resource("ec2")
    vpc = cli.Vpc(vpc_id)
    # Assume that we're using the default VPC which comes with a sg called "default" and
    # also assume that the SG has been configured to allow HTTP and HTTPS traffic globally
    sg_id = [sg.id for sg in list(vpc.security_groups.all()) if sg.group_name == "default"][0]
    # Assume to use default subnets of default VPC which are all public
    subnet_ids = [subnet.id for subnet in list(vpc.subnets.all())]
    vpc_details = VpcDetails(sg_id, subnet_ids)

    return vpc_details


def write_template(template: Template) -> None:
    template_dir = f"{os.getcwd()}/templates"
    if not os.path.exists(template_dir):
        os.mkdir(template_dir)
    template_file = f"{template_dir}/web.json"
    with open(template_file, "w") as f:
        f.write(template.to_json())


def make_template(
        name: str,
        replicas: int,
        docker_image: str,
        vpc_id: str,
) -> Template:
    vpc_deets = default_data(vpc_id)
    t = Template()
    t.set_description("Generic template for an ASG and Launch config")

    instances = t.add_parameter(Parameter(
        "Replicas",
        Type="Number",
        Description="Number of replicas",
        Default=int(replicas),
    ))

    container = t.add_parameter(Parameter(
        "DockerImage",
        Type="String",
        Description="Docker image to launch",
        Default=docker_image,
    ))

    lc = t.add_resource(autoscaling.LaunchConfiguration(
        "WebsiteLaunchConfig",
        # Ubuntu 18.04 server
        ImageId="ami-035966e8adab4aaad",
        # Free-tier
        InstanceType="t2.micro",
        SecurityGroups=[vpc_deets.security_group],
        UserData=Base64(
            Join(
                "",
                [
                    "#!/bin/bash\n",
                    "set -x\n",
                    "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -\n",
                    "sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu "
                    "$(lsb_release -cs) stable\"\n",
                    "sudo apt-get update\n",
                    "sudo apt-get install -y docker-ce docker-ce-cli containerd.io\n",
                    f"sudo docker run --name {name} -p 80:80 -p 443:443 --restart always ",
                    Ref(container),
                    "\n",
                    "sudo usermod -aG docker ubuntu\n",
                    "sudo reboot"
                ],
            ),
        ),
    ))

    t.add_resource(autoscaling.AutoScalingGroup(
        "WebsiteASG",
        AutoScalingGroupName=name,
        DesiredCapacity=Ref(instances),
        HealthCheckGracePeriod=300,
        LaunchConfigurationName=Ref(lc),
        MinSize=Ref(instances),
        MaxSize=Ref(instances),
        TerminationPolicies=["OldestInstance"],
        VPCZoneIdentifier=vpc_deets.subnet_ids,
    ))

    write_template(t)
    return t


def validate_template(client: boto3.client, template: Template) -> None:
    client.validate_template(
        TemplateBody=template.to_json()
    )


def launch_template(
    client: boto3.client,
    name: str,
    replicas: int,
    docker_image: str,
    template: Template
) -> None:
    client.create_stack(
        StackName=name,
        TemplateBody=template.to_json(),
        Parameters=[
            {
                "ParameterKey": "Replicas",
                "ParameterValue": str(replicas),
            },
            {
                "ParameterKey": "DockerImage",
                "ParameterValue": docker_image,
            },
        ],
    )


def deploy(
    name: str,
    replicas: int,
    docker_image: str,
    vpc_id: str,
) -> None:
    template = make_template(name, replicas, docker_image, vpc_id)
    cf_cli = boto3.client("cloudformation")
    validate_template(cf_cli, template)
    launch_template(cf_cli, name, replicas, docker_image, template)
