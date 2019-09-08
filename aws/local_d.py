# docker run -p 8000:8000 amazon/dynamodb-local
# pip install click boto3

import click
import boto3
from botocore.exceptions import ClientError

client = None

@click.option('--ip', default='localhost')
@click.option('--port', default='8000')
@click.option('--region', default='eu-west-1')
@click.option('--secret', default='x')
@click.option('--key', default='x')
@click.option('--protocol', default='http')
@click.option('--ssl', default=False)
@click.group()
@click.pass_context
def cli(ctx, ip, port, region, secret, key, protocol, ssl):
    ctx.obj['IP'] = ip
    ctx.obj['PORT'] = port
    ctx.obj['PROTOCOL'] = protocol
    global client
    client = boto3.client('dynamodb',
                        endpoint_url=protocol + '://' + ip + ':' + port,
                        region_name=region,
                        aws_secret_access_key=secret,
                        aws_access_key_id=key,
                        use_ssl=ssl)
    pass

@cli.command()
@click.argument('name')
@click.option('--attribute', '-a', multiple=True, type=(str, str, str), help='Attributes with type and key type triplets')
@click.pass_context
def create(ctx, name, attribute):
    attributeDefinitions = []
    keyDefinitions = []

    for atr in attribute:
        atrName, atrType, keyType = atr
        attributeDefinitions.append({
            'AttributeName': atrName,
            'AttributeType': atrType
        })
        keyDefinitions.append({
            'AttributeName': atrName,
            'KeyType': keyType
        })
    try:
        client.create_table(
            AttributeDefinitions = attributeDefinitions,
            TableName = name,
            KeySchema = keyDefinitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 123,
                'WriteCapacityUnits': 123
            })
        click.echo('Table "' + name + '" created')
    except ClientError as e:
        if 'ResourceInUseException' == e.__class__.__name__:
            click.echo('Table "' + name + '" already exists')
        else:
            raise e


@cli.command()
@click.pass_context
def listt(ctx):
    click.echo(client.list_tables().get('TableNames', 'No queues'))

@cli.command()
@click.argument('name')
@click.option('--key', '-k', multiple=True, type=(str,str,str), help='Key, key type, key value triplet')
@click.option('--projection', '-p', multiple=False, type=(str), help='Projection expresion')
@click.option('--expression', '-e', multiple=True, type=(str,str), help='Expression attribute name')
@click.pass_context
def get(ctx, name, key, expression, projection):
    keyDefinition = {}

    for k in key:
        keyName, keyType, keyValue = k
        keyDefinition[keyName] = { keyType: keyValue }

    expressionAttributeNames = {}

    for e in expression:
        expressionName, expressionValue = e
        expressionAttributeNames[expressionName] = expressionValue

    click.echo(client.get_item(TableName=name, Key=keyDefinition,
                                ProjectionExpression=projection,
                                ExpressionAttributeNames=expressionAttributeNames
        ).get('Item', 'No items found'))

@cli.command()
@click.argument('name')
@click.option('--item', '-i', multiple=True, type=(str,str,str), help='Item name, item type, item value triplet')
@click.pass_context
def add(ctx, name, item):
    itemToAdd = {}

    for i in item:
        itemName, itemType, itemValue = i
        itemToAdd[itemName] = { itemType: itemValue }

    click.echo(itemToAdd)

    click.echo(client.put_item(TableName=name, Item=itemToAdd))

if __name__ == '__main__':
    cli(obj={})
