import boto3


class S3BucketManager:
    def __init__(self, id, key, file_name, bucket_name):
        self.bucket_name = bucket_name
        self.file_name = file_name
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

    def write_file(self, message):
        with open(self.file_name, "a", encoding='utf-8') as f:
            f.write("\n" + message)
        print(f"[{self.file_name}] write(append) success.")

    def update_bucket(self):
        self.client.upload_file(self.file_name, self.bucket_name, self.file_name)
        print(f'bucket_name = {self.bucket_name}, file = {self.file_name} is successfully updated.')

    def read_bucket(self):
        obj = self.s3.Object(self.bucket_name, self.file_name)
        body = obj.get()["Body"].read()
        print(f'bucket_name = {self.bucket_name}, file = {self.file_name} is successfully downloaded.')
        return body.decode()

    def clear_bucket(self):
        with open(self.file_name, "w") as f:
            f.write("")
        print(f"[{self.file_name}] all data cleared.")
        self.update_bucket()

