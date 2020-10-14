# *_*coding:utf-8 *_*

from qiniu import Auth, put_data, etag
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = 'XWpKUq8m37700E9LyIaouLeTg6xqBxztTa3n3Nli'
secret_key = 'P4xpj0CVf4BVZ4wqC-36HHcFOuE06zwg9x7VXVIN'


def storage(file_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihome'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)


    ret, info = put_data(token, None, file_data)

    # print(info)
    # print("*"*20)
    # print(ret)

    if info.status_code == 200:
        #表示上传成功
        return ret.get("key")
    else:
        raise Exception("上传图片失败")


if __name__ == '__main__':
    with open("./1.jpg", "rb") as f:
        file_data = f.read()
        storage(file_data)