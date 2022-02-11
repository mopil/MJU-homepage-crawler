import boto3


class S3BucketManager:
    def __init__(self, id, key, bucket_name, file_name):
        self.file_name = file_name
        self.bucket_name = bucket_name
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=id,
            aws_secret_access_key=key
            )
        self.client = boto3.client(
            's3',
            aws_access_key_id=id,
            aws_secret_access_key=key
            )
        print("s3 bucket successfully connected.")

    def write_file(self, message, mode):
        with open(self.file_name, mode, encoding='utf-8') as f:
            f.write(message + "\n")
        self.client.upload_file(self.file_name, self.bucket_name, self.file_name)

    def read_file(self):
        obj = self.s3.Object(self.bucket_name, self.file_name)
        body = obj.get()["Body"].read()
        #print(f'{file_name} is successfully read.')
        return body.decode()

    def clear_file(self):
        self.write_file("", "w")
        print(f'{self.file_name} all data reset complete.')

