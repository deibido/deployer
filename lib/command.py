import click

from lib.ec2 import deploy as ec2_deploy
from lib.s3 import deploy as s3_deploy, teardown as s3_teardown, update as s3_update


class OptionError(BaseException):
    pass


@click.group(help="Deploy to AWS")
def run() -> None:
    pass


@run.command()
@click.option("--mode", help="Operation mode", prompt="Create, update or delete")
@click.option("--bucket-name", help="Specify the bucket name.", prompt="Bucket name")
def s3(
        mode: str,
        bucket_name: str,
) -> None:
    if mode.lower() == "create":
        s3_deploy(bucket_name)
        print(f"Website can be found at: http://{bucket_name}.s3-website-eu-west-1.amazonaws.com/")
    elif mode.lower() == "update":
        s3_update(bucket_name)
        print("Website successfully updated")
    elif mode.lower() == "delete":
        s3_teardown(bucket_name)
        print("Website successfully torn down.")
    else:
        raise OptionError("Did not specify a suitable mode of operation: Create, Update or Delete")

# FIXME: Remove testing defaults
@run.command()
@click.option("--mode", help="Operation mode", prompt="Create, update or delete", default="create")
@click.option("--project-name", help="Specify the project name.", prompt="Project name", default="sloth-online")
@click.option("--replicas", help="Number of replicas (for HA)", prompt="Replicas", default=1)
@click.option("--docker-image", help="Docker image to deploy", prompt="Docker image (<REPO>/<IMAGE>:<TAG>)", default="davesz/sloth-online")
@click.option("--vpc-id", help="VPC in which to deploy the service", prompt="VPC ID", default="vpc-3d658f44")
def ec2(
        mode: str,
        project_name: str,
        replicas: int,
        docker_image: str,
        vpc_id: str
) -> None:

    if mode.lower() == "create":
        ec2_deploy(
            project_name,
            int(replicas),
            docker_image,
            vpc_id
        )

#
# @click.command()
# @click.option("--asg-name", help="Name of the ASG to scale", prompt="Auto-scaling group name:")
# def scale(
#         asg_name: str,
# ) -> str:
#
#     print(service + " " + tmp)
#     return service + tmp
