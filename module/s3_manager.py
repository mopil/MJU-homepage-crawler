import boto3


class S3Manager:
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

    def duplication_filtering(self, crawled_result):
        filtered_result = []
        stored_notice = self.read_file()  # stored_notice = type : str
        for notice in crawled_result:
            title = notice[0]
            if title not in stored_notice:
                self.write_file(title, "a")
                filtered_result.append(notice)
        return filtered_result

