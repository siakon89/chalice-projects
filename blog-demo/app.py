from chalice import Chalice
import boto3
from boto3.dynamodb.conditions import Key


app = Chalice(app_name='blog-demo')
dynamodb = boto3.resource("dynamodb", region_name='eu-central-1')
table = dynamodb.Table('blog-demo-1')


@app.route('/', methods=['GET'])
def index():
    response = table.scan()
    data = response.get('Items', None)

    return {'data': data}


@app.route('/item/{id}', methods=['GET'])
def item_get(id):
    response = table.query(
        KeyConditionExpression=Key("id").eq(id)
    )
    data = response.get('Items', None)

    return {'data': data}


@app.route('/item', methods=['POST'])
def item_set():
    data = app.current_request.json_body

    try:
        table.put_item(Item={
            "id": data['id'],
            "text": data['text']
        })

        return {'message': 'ok', 'status': 201, "id": data['id']}
    except Exception as e:
        return {'message': str(e)}
