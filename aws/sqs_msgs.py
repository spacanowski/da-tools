# pip install click boto3
# example:
# python sqs_msgs.py --url https://sqs.eu-west-1.amazonaws.com/<acc_id> --region eu-west-1 --ssl True --count 25 --key <key> --secret <secret> copy/move <source-queue-name> <target-queue-name>

import click
import boto3

client = None


@click.option('--url', default='http://localhost:9324/queue/etltest')
@click.option('--region', default='elasticmq')
@click.option('--secret', default='x')
@click.option('--key', default='x')
@click.option('--ssl', default=False)
@click.option('--count', default=0, help='Number of msgs. Default is all.')
@click.group()
@click.pass_context
def cli(ctx, url, region, secret, key, ssl, count):
    ctx.obj['URL'] = url
    ctx.obj['COUNT'] = count
    global client
    client = boto3.client('sqs',
                        endpoint_url=url,
                        region_name=region,
                        aws_secret_access_key=secret,
                        aws_access_key_id=key,
                        use_ssl=ssl)
    pass


@cli.command()
@click.argument('source', nargs=1)
@click.argument('target', nargs=1)
@click.pass_context
def copy(ctx, source, target):
    execute(ctx, source, target, noOpDelete)


@cli.command()
@click.argument('source', nargs=1)
@click.argument('target', nargs=1)
@click.pass_context
def move(ctx, source, target):
    execute(ctx, source, target, deleteBatch)


def execute(ctx, source, target, deleteMethod):
    url = ctx.obj['URL']
    count = ctx.obj['COUNT']

    if count <= 0:
        count = int(msgsno(client, url + '/' + source))

    for batch in range(0, count, 10):
        batchSize = 10

        if count - batch < 10:
            batchSize = count - batch

        msgs = client.receive_message(QueueUrl=url + '/' + source,
                                        MaxNumberOfMessages=batchSize,
                                        VisibilityTimeout=6000).get('Messages')
        if msgs:
            entries = list(map(lambda x: {
                                            'Id': x.get('MessageId'),
                                            'MessageBody': x.get('Body'),
                                            'DelaySeconds': 0
                                        }, msgs))

            client.send_message_batch(QueueUrl=url + '/' + target, Entries=entries)
            deleteMethod(url, source, msgs)
            click.echo('sent: ' + str(batch + batchSize) + ' messages from ' + str(count) + '\n')
        else:
            click.echo('No msgs on source queue')
            break


def msgsno(client, queueUrl):
    return client.get_queue_attributes(QueueUrl=queueUrl,
                                        AttributeNames=['ApproximateNumberOfMessages']).get('Attributes', {}).get('ApproximateNumberOfMessages', 0)


def deleteBatch(url, source, msgs):
    entries = list(map(lambda x: {
                                        'Id': x.get('MessageId'),
                                        'ReceiptHandle': x.get('ReceiptHandle')
                                }, msgs))
    client.delete_message_batch(QueueUrl=url + '/' + source, Entries=entries)


def noOpDelete(url, source, msgs):
    return


if __name__ == '__main__':
    cli(obj={})
