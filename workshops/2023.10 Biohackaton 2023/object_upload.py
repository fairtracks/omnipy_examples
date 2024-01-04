import boto3


def upload_to_bucket(file_path):
    #session = boto3.Session(profile_name='minio')
    session = boto3.Session()
    s3 = session.resource(
        service_name='s3',
        aws_access_key_id='accesskeyexample123',
        aws_secret_access_key='secretkeyexample123',
        endpoint_url='https://omnipy.fairtracks.sigma2.no')

    bucket = s3.Bucket('testbucket')
    bucket.upload_file(file_path, file_path.split('/')[-1])


if __name__ == "__main__":
    file_path = "./testfile.txt"
    upload_to_bucket(file_path)
