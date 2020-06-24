import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import math

# Overwrite is true, and will infer file type. So make sure to_filename is only the name of the file, don't include the extension
def download_image_from_url(url_image, to_filename_with_no_extension):
    try:
        response = requests.get(url_image, stream=True)
    except Exception as e:
        raise ValueError( "ERROR: download_image_from_url(): Exception - {}".format(e) )

    if response.status_code != 200:
        raise ValueError( "ERROR: download_image_from_url(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )

    try:
        main_type, sub_type = response.headers['Content-Type'].split("/")
        image_len = response.headers['Content-Length']
    except Exception as e:
        raise ValueError( "ERROR: download_image_from_url(): Exception - {}".format(e) )

    if main_type != 'image':
        raise ValueError( "ERROR: download_image_from_url(): Returned Content-Type is not image. Instead it is {}".format(main_type) )

    try:
        image_len = int(image_len)
    except Exception as e:
        raise ValueError( "ERROR: download_image_from_url(): Exception - {}".format(e) )

    if not isinstance(image_len, int):
        raise ValueError( "ERROR: download_image_from_url(): Returned Content-Length is not an int. Instead it is {}".format(type(image_len)) )


    to_filename_full = to_filename_with_no_extension + "." + sub_type
    print(to_filename_full)
    print()

    print(response.headers)
    print()

    with open(file=to_filename_full, mode='w') as handle:
        for block in tqdm(response.iter_content(1024), total=math.ceil(image_len/1024)):
            if not block:
                break
            handle.write(block)

def scrap_for_current_image_link(url_sub_profile):
    response = requests.get(url_sub_profile)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )

    # image_div = soup.find_all(name='img', class_='_1izoQ')
    image_div = soup.find(name='img', class_='_1izoQ')
    if image_div is None:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Cannot find a single <img class='_1izoQ'> occurence" )

    try:
        image_link = image_div["src"]
    except Exception as e:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Exception - {}".format(e) )
    if image_link is None:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Cannot find attr 'src' in {}".format(image_div) )

    title_div = soup.find(name='h1', attrs={'data-hook': 'deviation_title'})
    if title_div is None:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Cannot find a single <h1 data-hook='deviation_title'> occurence" )

    try:
        title = title_div.contents[0]
    except Exception as e:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Exception - {}".format(e) )
    if title is None:
        raise ValueError( "ERROR: scrap_for_current_image_link(): Cannot find any content in {}".format(title_div) )


    # attributes_dictionary = soup.find('h1').attrs
    # print(attributes_dictionary)

    # print()
    print("title_div: \t{}".format(title_div))
    print("title: \t\t{}".format(title))
    # print()

    return image_link, title

# only download highest quality of the public downloadable images
def download_all_image_from_profile_link(url_profile):
    print()

def main():
    url = r'https://www.deviantart.com/arsenixc/art/Wentmon-845001018'
    # url = r'https://www.deviantart.com/arsenixc/art/Imperial-city-839848270'
    image_link, image_title = scrap_for_current_image_link(url)

    # print(image_link)
    # print(image_title)
    # print()
    download_image_from_url(url_image=image_link, to_filename_with_no_extension=image_title)


if __name__ == '__main__':
    main()