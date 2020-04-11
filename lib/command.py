import click


def abort(ctx, param, value)

@click.group(help="Deploy to AWS")
def run() -> None:
    pass


@click.command()
@click.option("--bucket-name", help="Specify the bucket name:", prompt="Bucket name:")
def s3(
        service: str,
) -> str:

    return service


@click.command()
@click.option("--bucket-name", help="Specify the bucket name:", prompt="Bucket name:")
def s3(
        service: str,
) -> str:

    print(service + " " + tmp)
    return service + tmp


@click.command()
@click.option("--bucket-name", help="Specify the bucket name:", prompt="Bucket name:")
def scale(
        service: str,
) -> str:

    print(service + " " + tmp)
    return service + tmp
