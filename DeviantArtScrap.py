import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import math
import json

# Return the dict of the json file
def decode_json_config_file_to_dict( filepath='' ):
    if filepath == '':
        print('ERROR: decode_json_config_file_to_dict(): Arg filepath is empty string')
        return None

    try:
        f = open(filepath)
        data = json.load(f)
        return data
    except Exception as e:
        print('ERROR: decode_json_config_file_to_dict(): Fail to open {}'.format(filepath), e)
        return None

    return None

# Only works for first level of variables, for now, until multiple level is implemented
def get_single_variable_from_json_file( filepath='', arg_name='' ):
    if filepath == '':
        print('ERROR: get_single_variable_from_json_file(): Arg filepath is empty string')
        return None

    if arg_name == '':
        print('ERROR: get_single_variable_from_json_file(): Arg arg_name is empty string')
        return None

    json_dict = decode_json_config_file_to_dict(filepath=filepath)
    if not isinstance(json_dict, dict):
        print('ERROR: get_single_variable_from_json_file(): The file is not a correctly structured json file')
        return None
    else:
        if arg_name in json_dict:
            return json_dict[arg_name]
        else:
            print('ERROR: get_single_variable_from_json_file(): The key "{}" does not exists in dictionary from the json file'.format(arg_name))
            return None

    return None

# Overwrite is not true, will skip if it's the case. And will infer file type. So make sure to_filename is only the name of the file, don't include the extension
def download_image_from_url(url_image, to_filename_with_no_extension, to_dir_path):
    try:
        response = requests.get(url_image, stream=True)
    except Exception as e:
        raise ValueError( " ERROR: download_image_from_url(): Exception - {}".format(e) )

    if response.status_code != 200:
        raise ValueError( " ERROR: download_image_from_url(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )

    try:
        main_type, sub_type = response.headers['Content-Type'].split("/")
        image_len = response.headers['Content-Length']
    except Exception as e:
        raise ValueError( " ERROR: download_image_from_url(): Exception - {}".format(e) )

    if main_type != 'image':
        raise ValueError( " ERROR: download_image_from_url(): Returned Content-Type is not image. Instead it is {}".format(main_type) )

    try:
        image_len = int(image_len)
    except Exception as e:
        raise ValueError( " ERROR: download_image_from_url(): Exception - {}".format(e) )

    if not isinstance(image_len, int):
        raise ValueError( " ERROR: download_image_from_url(): Returned Content-Length is not an int. Instead it is {}".format(type(image_len)) )

    # Determining unix style or window style path
    if to_dir_path[-1] != '/' and to_dir_path[-1] != '\\':
        if '/' in to_dir_path:
            to_dir_path = to_dir_path + '/'
        elif '\\' in to_dir_path:
            to_dir_path = to_dir_path + '\\'
        else:
            # Take a leap of faith here, going with my favorite style, unix path style
            to_dir_path = to_dir_path + '\\'

    to_path_filename_full = to_dir_path + to_filename_with_no_extension + "." + sub_type

    try:
        print( ' {}'.format(to_path_filename_full) )
        with open(file=to_path_filename_full, mode='xb') as handle:
            for block in tqdm(response.iter_content(1024), total=math.ceil(image_len/1024)):
                if not block:
                    break
                handle.write(block)
    except FileExistsError:
        print( " \tFilename already exists, skipping" )
    except Exception as e:
        raise ValueError( " ERROR: download_image_from_url(): Exception - {}".format(e) )


# Will replace any space in title with underscore_
def scrap_for_current_image_link_and_title(url_art):
    response = requests.get(url_art)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )

    # image_div = soup.find_all(name='img', class_='_1izoQ')
    image_div = soup.find(name='img', class_='_1izoQ')
    if image_div is None:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Cannot find a single <img class='_1izoQ'> occurence" )

    try:
        image_link = image_div["src"]
    except Exception as e:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Exception - {}".format(e) )
    if image_link is None:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Cannot find attr 'src' in {}".format(image_div) )

    title_div = soup.find(name='h1', attrs={'data-hook': 'deviation_title'})
    if title_div is None:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Cannot find a single <h1 data-hook='deviation_title'> occurence" )

    try:
        title = title_div.contents[0]
    except Exception as e:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Exception - {}".format(e) )
    if title is None:
        raise ValueError( " ERROR: scrap_for_current_image_link_and_title(): Cannot find any content in {}".format(title_div) )

    title = title.replace(' ','_')

    return image_link, title

# Return a list of art links for an artist and the artist name
def scrap_for_all_art_link_from_profile_link(url_profile):
    response = requests.get(url_profile)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )

    url_arts = soup.find_all(name='a', attrs={'data-hook': 'deviation_link'})
    if url_arts is None:
        raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Cannot find a single <img class='_1izoQ'> occurence" )

    print(url_arts)

    artist_name=""

    return artist_name, url_arts

def main():
    config_path = r'./config.json'

    download_dir = get_single_variable_from_json_file( config_path, "download_dir" )
    print(download_dir)

    url_list = [
        r'https://www.deviantart.com/arsenixc/art/Wentmon-845001018',
        r'https://www.deviantart.com/arsenixc/art/Imperial-city-839848270',
        r'https://www.deviantart.com/arsenixc/art/Arvez-and-Arinly-444904429',
    ]

    print( ' Downloading for artist {}'.format("arsenixc") )
    for url in url_list:
        image_link, image_title = scrap_for_current_image_link_and_title(url)

        download_image_from_url(url_image=image_link, to_filename_with_no_extension=image_title, to_dir_path=download_dir)


if __name__ == '__main__':
    main()