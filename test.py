import requests, response

response = requests.post(
    'http://localhost:5000',
    data={
		consumer_key='8Vj4ZDcZXBT31XNMtHX3vOU2ZmHOUbbx9OwymBTX',
		consumer_secret='RddFmLDsDAr3PKgAMcDB5ikx3VAkG3VdqSsPjTShYWQDePYmnH',
		base_url='http://127.0.0.1:5000/api/',
		request_token_url='http://127.0.0.1:5000/oauth/request_token',
		access_token_method='GET',
		access_token_url='http://127.0.0.1:5000/oauth/access_token',
		authorize_url='http://127.0.0.1:5000/oauth/authorize',
    }
)

print(response.text)