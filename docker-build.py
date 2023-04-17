import os

# Define the image name and tag
image_name = 'ssenchyna/snmp'
# docker buildx create --use
os.system(
    f"docker buildx build --platform linux/amd64,linux/arm64 -t {image_name} --push .")
# os.system(
#     f"docker build -t {image_name} .")
