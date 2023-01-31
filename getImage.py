from functools import partial
import requests
import os
import multiprocessing
import time
from tqdm import tqdm

baseDir = os.path.dirname(os.path.abspath(__file__))


def init():
    global baseDir
    baseDir = os.path.dirname(os.path.abspath(__file__))
    baseDir = input("Please input the base directory: ")
    # Check baseDir valid
    if not os.path.exists(baseDir):
        baseDir = os.path.dirname(os.path.abspath(__file__))
        print("Invalid baseDir, use default value: " + baseDir)


# Download the images
def download(url, envir):
    name = url.split('/')[-1]
    path = os.path.join(envir[1], "img"+envir[0], name)
    if os.path.exists(path):
        # print("Existed image: " + path)
        return
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
                f.close()
                # print("Downloaded image: " + name + "to " + path)
    finally:
        time.sleep(0.4)
        download(url, envir)


# Create a folder to save the images
def saveDir():
    global baseDir
    if not os.path.exists(os.path.join(baseDir, "imgpc")):
        os.mkdir(os.path.join(baseDir, "imgpc"))
    if not os.path.exists(os.path.join(baseDir, "imgmp")):
        os.mkdir(os.path.join(baseDir, "imgmp"))
    if not os.path.exists(os.path.join(baseDir, "imgrandom")):
        os.mkdir(os.path.join(baseDir, "imgrandom"))

# Get the image URL when more than 100 images are needed


def getUrlRecursion(num, picType):
    # print("Sleep time: " + str(0.4))
    # Divide the number of images into 100 each time
    if num > 100:
        urlList = getUrl(100, picType)
        num -= 100
        # Sleep for a while
        time.sleep(0.4)
        return urlList + getUrlRecursion(num, picType)
    else:
        urlList = getUrl(num, picType)
        # Sleep for a while
        time.sleep(0.4)
        return urlList


# Get the image URL
def getUrl(num, picType):
    # Check if the number of images is valid, max 100
    if num > 100:
        print("The number of images is too large, max 100")
        num = 100
    elif num < 1:
        print("The number of images is too small, min 1")
        num = 1
    # Get the image URL
    url = 'https://iw233.cn/api.php?sort=' + \
        picType + '&type=json&num=' + str(num)
    html = requests.get(url).json()
    urlList = html['pic']
    return urlList


# Main function
def main():
    global baseDir
    # Create a folder to save the images
    saveDir()
    # Get the image URL
    # Check if it is necessary to get the image URL recursively
    numImages = int(input("How many images do you want to download? "))
    picType = int(
        input("Which type of images do you want to download? (1.pc/2.mp/3.random)"))
    # Check if the picType is valid
    if picType == 1:
        picType = "pc"
    elif picType == 2:
        picType = "mp"
    elif picType == 3:
        picType = "random"
    else:
        print("Invalid picType, use default value: pc")
        picType = "pc"
    numProcess = int(input("How many processes do you want to use? "))
    if numImages > 100:
        urlList = []
        for i in tqdm(range(numImages//100), desc="Getting URL"):
            urlList += getUrlRecursion(100, picType)
            time.sleep(0.4)

    else:
        urlList = getUrl(numImages, picType)
    # Download the images with multi-processing
    with multiprocessing.Pool(numProcess) as p:
        result = list(tqdm(p.imap(partial(download, envir=[picType,baseDir]),
                      urlList), total=len(urlList), desc="Downloading Images"))


if __name__ == '__main__':
    init()
    print(baseDir)
    main()
