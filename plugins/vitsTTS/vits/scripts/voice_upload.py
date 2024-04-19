from google.colab import files
import shutil
import os
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, required=True, help="type of file to upload")
    args = parser.parse_args()
    file_type = args.type

    basepath = os.getcwd()
    uploaded = files.upload() # 上传文件
    assert(file_type in ['zip', 'audio', 'video'])
    if file_type == "zip":
        upload_path = "./custom_character_voice/"
        for filename in uploaded.keys():
            #将上传的文件移动到指定的位置上
            shutil.move(os.path.join(basepath, filename), os.path.join(upload_path, "custom_character_voice.zip"))
    elif file_type == "audio":
        upload_path = "./raw_audio/"
        for filename in uploaded.keys():
            #将上传的文件移动到指定的位置上
            shutil.move(os.path.join(basepath, filename), os.path.join(upload_path, filename))
    elif file_type == "video":
        upload_path = "./video_data/"
        for filename in uploaded.keys():
            # 将上传的文件移动到指定的位置上
            shutil.move(os.path.join(basepath, filename), os.path.join(upload_path, filename))