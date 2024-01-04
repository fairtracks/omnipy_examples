import boto3


def list_buckets():
    #session = boto3.session.Session(profile_name='minio')

    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        aws_access_key_id='accesskeyexample123',
        aws_secret_access_key='secretkeyexample123',
        endpoint_url='https://omnipy.fairtracks.sigma2.no',
        use_ssl=True)

    response = s3.list_buckets()

    return [bucket['Name'] for bucket in response['Buckets']]


buckets = list_buckets()
for bucket in buckets:
    print(bucket)
