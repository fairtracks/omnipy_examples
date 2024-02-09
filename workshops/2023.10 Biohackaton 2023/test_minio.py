import boto3

session = boto3.session.Session(profile_name='minio')

s3_client = session.client(
    service_name='s3',
    endpoint_url='https://minio-test2.fairtracks.sigma2.no',
)

buckets = s3_client.list_buckets()
for bucket in buckets['Buckets']:
    bucket_name = bucket['Name']
    print(f"Bucket: {bucket_name}")
    print(s3_client.list_objects(Bucket=bucket_name).get('Contents', []))
    for obj in s3_client.list_objects(Bucket=bucket_name).get('Contents', []):
        print(obj['Key'])
