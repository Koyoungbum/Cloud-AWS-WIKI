import json
import boto3
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Categories')  # DynamoDB 테이블 이름 'Categories'

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod')

        if not http_method:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid request, httpMethod missing'})
            }

        # GET 요청: 카테고리 목록 가져오기
        if http_method == 'GET':
            response = table.scan()  # DynamoDB에서 모든 카테고리 데이터를 조회
            items = response.get('Items', [])
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
                },
                'body': json.dumps({'Items': items})  # 카테고리 목록을 반환
            }

        # POST 요청: 카테고리 추가
        elif http_method == 'POST':
            body = json.loads(event['body'])
            category_name = body.get('categoryName')
            content = body.get('content')

            # 카테고리 이름과 내용이 필요한지 확인
            if not category_name or not content:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
                    },
                    'body': json.dumps({'message': '카테고리 이름과 내용은 필수입니다.'})
                }

            # 새로운 카테고리 생성
            item = {
                'categoryName': category_name,
                'content': content,
                'id': str(uuid4())  # 고유 ID 추가
            }
            table.put_item(Item=item)

            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
                },
                'body': json.dumps({
                    'message': '새 카테고리가 성공적으로 추가되었습니다.',
                    'categoryName': category_name
                })
            }

        # PUT 요청: 카테고리 수정
        elif http_method == 'PUT':
            body = json.loads(event['body'])
            category_name = body.get('categoryName')
            content = body.get('content')

            # 수정할 카테고리 이름과 내용이 필요한지 확인
            if not category_name or not content:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
                    },
                    'body': json.dumps({'message': '카테고리 이름과 내용은 필수입니다.'})
                }

            # 카테고리를 찾고 업데이트
            response = table.get_item(Key={'categoryName': category_name})
            item = response.get('Item')

            if not item:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
                    },
                    'body': json.dumps({'message': '카테고리를 찾을 수 없습니다.'})
                }

            # 업데이트된 내용으로 수정
            item['content'] = content
            table.put_item(Item=item)

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
                },
                'body': json.dumps({'message': '카테고리가 성공적으로 수정되었습니다.'})
            }

        # 잘못된 요청에 대한 처리
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid request'})
        }

    except Exception as error:
        print(f"Error: {error}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS 헤더 추가
            },
            'body': json.dumps({
                'message': '서버 오류',
                'error': str(error)
            })
        }
