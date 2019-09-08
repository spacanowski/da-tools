# docker run -dp 9324:9324 vsouza/sqs-local
# pip install click boto3

import click
import boto3

client = None

@click.option('--ip', default='localhost')
@click.option('--port', default='9324')
@click.option('--path', default='queue')
@click.option('--region', default='elasticmq')
@click.option('--secret', default='x')
@click.option('--key', default='x')
@click.option('--protocol', default='http')
@click.option('--ssl', default=False)
@click.group()
@click.pass_context
def cli(ctx, ip, port, path, region, secret, key, protocol, ssl):
    ctx.obj['IP'] = ip
    ctx.obj['PORT'] = port
    ctx.obj['PROTOCOL'] = protocol
    ctx.obj['PATH'] = path
    global client
    client = boto3.client('sqs',
                        endpoint_url=protocol + '://' + ip + ':' + port,
                        region_name=region,
                        aws_secret_access_key=secret,
                        aws_access_key_id=key,
                        use_ssl=ssl)
    pass

@cli.command()
@click.argument('name')
@click.pass_context
def create(ctx, name):
    click.echo(client.create_queue(QueueName=name).get('QueueUrl', 'Creation failed'))

@cli.command()
@click.argument('name')
@click.pass_context
def delq(ctx, name):
    ip = ctx.obj['IP']
    port = ctx.obj['PORT']
    protocol = ctx.obj['PROTOCOL']
    path = ctx.obj['PATH']
    response = client.delete_queue(QueueUrl=protocol + '://' + ip + ':' + port +'/' + path + '/' + name)
    click.echo('done' if response.get('ResponseMetadata').get('HTTPStatusCode') == 200 else 'failed')

@cli.command()
@click.pass_context
def listq(ctx):
    click.echo(client.list_queues().get('QueueUrls', 'No queues'))

@cli.command()
@click.argument('name')
@click.pass_context
def purge(ctx, name):
    ip = ctx.obj['IP']
    port = ctx.obj['PORT']
    protocol = ctx.obj['PROTOCOL']
    path = ctx.obj['PATH']
    response = client.purge_queue(QueueUrl=protocol + '://' + ip + ':' + port +'/' + path + '/' + name)
    click.echo('done' if response.get('ResponseMetadata').get('HTTPStatusCode') == 200 else 'failed')

@cli.command()
@click.argument('name')
@click.pass_context
def url(ctx, name):
    click.echo(client.get_queue_url(QueueName=name).get('QueueUrl'))

@cli.command()
@click.argument('name')
@click.option('--count', default=1, help='Number of msgs. Default is 1.')
@click.option('--timeout', default=30, help='Visibility timeout in seconds. Default is 30.')
@click.pass_context
def recieve(ctx, name, count, timeout):
    ip = ctx.obj['IP']
    port = ctx.obj['PORT']
    protocol = ctx.obj['PROTOCOL']
    path = ctx.obj['PATH']
    msgs = client.receive_message(QueueUrl=protocol + '://' + ip + ':' + port +'/' + path + '/' + name,
                                    MaxNumberOfMessages=count,
                                    VisibilityTimeout=timeout).get('Messages')
    if msgs:
        for m in msgs:
            click.echo('msgId: ' + m.get('MessageId') + ',\nreceiptHandle: ' + m.get('ReceiptHandle') + ',\nbody: ' + m.get('Body') + '\n')
    else:
        click.echo('No msgs on queue')

@cli.command()
@click.argument('name')
@click.argument('receiptHandle')
@click.pass_context
def delm(ctx, name, receiptHandle):
    ip = ctx.obj['IP']
    port = ctx.obj['PORT']
    protocol = ctx.obj['PROTOCOL']
    path = ctx.obj['PATH']
    click.echo(client.delete_message(QueueUrl=protocol + '://' + ip + ':' + port +'/' + path + '/' + name, ReceiptHandle=receiptHandle))

@cli.command()
@click.argument('name')
@click.pass_context
def msgsno(ctx, name):
    ip = ctx.obj['IP']
    port = ctx.obj['PORT']
    protocol = ctx.obj['PROTOCOL']
    path = ctx.obj['PATH']
    click.echo(client.get_queue_attributes(QueueUrl=protocol + '://' + ip + ':' + port +'/' + path + '/' + name,
                                            AttributeNames=['ApproximateNumberOfMessages']).
                        get('Attributes', {}).
                        get('ApproximateNumberOfMessages', 0))

if __name__ == '__main__':
    cli(obj={})
