import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import math
import json
from datetime import datetime

# Taken from https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python
def get_duration( then, now = datetime.now(), interval = "default" ):

    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    duration = now - then # For build-in functions
    duration_in_s = duration.total_seconds()

    def years():
      return divmod(duration_in_s, 31536000) # Seconds in a year=31536000.

    def days(seconds = None):
      return divmod(seconds if seconds != None else duration_in_s, 86400) # Seconds in a day = 86400

    def hours(seconds = None):
      return divmod(seconds if seconds != None else duration_in_s, 3600) # Seconds in an hour = 3600

    def minutes(seconds = None):
      return divmod(seconds if seconds != None else duration_in_s, 60) # Seconds in a minute = 60

    def seconds(seconds = None):
      if seconds != None:
        return divmod(seconds, 1)
      return duration_in_s

    # Give you all the correct granular info
    def totalDuration():
        y = years()
        d = days(y[1]) # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])

        return "{} years, {} days, {} hours, {} minutes and {} seconds".format(int(y[0]), int(d[0]), int(h[0]), int(m[0]), int(s[0]))

    return {
        'years': int(years()[0]),
        'days': int(days()[0]),
        'hours': int(hours()[0]),
        'minutes': int(minutes()[0]),
        'seconds': int(seconds()),
        'default': totalDuration()
    }[interval]

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
        print( ' {}'.format(to_filename_with_no_extension) )
        with open(file=to_path_filename_full, mode='xb') as handle:
            for block in tqdm(response.iter_content(1024), total=math.ceil(image_len/1024)):
                if not block:
                    break
                handle.write(block)
    except FileExistsError:
        print( " \tskipping, filename already exists" )
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

# Return a list of art links and the artist name for an artist
def scrap_for_all_art_link_from_profile_link(url_profile):
    response = requests.get(url_profile)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )

    tag_arts = soup.find_all(name='a', attrs={'data-hook': 'deviation_link', 'href': re.compile(".*/art/.*")})
    if tag_arts is None:
        raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Cannot find a single <a data-hook='deviation_link' */art/*> occurence" )

    url_arts=[]

    for each_tag in tag_arts:
        try:
            url_arts.append(each_tag["href"])
        except Exception as e:
            raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Exception - {}".format(e) )

    if len(url_arts) == 0:
        raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Cannot find attr 'href' in {}".format(each_tag) )

    tag_artist = soup.find(name='a', attrs={'data-username': re.compile(".*")})
    artist_name = tag_artist["data-username"]

    if len(artist_name) == 0:
        raise ValueError( " ERROR: scrap_for_all_art_link_from_profile_link(): Cannot find artist name in {}".format(tag_artist) )

    return artist_name, url_arts

# Return the artist name for the art link
def scrap_for_artist_name_from_art_link(url_art):
    response = requests.get(url_art)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        raise ValueError( " ERROR: scrap_for_artist_name_from_art_link(): Returned status code is not 200. Instead it is {}: {}".format(response.status_code, response.reason) )


    tag_artist = soup.find(name='a', attrs={'data-username': re.compile(".*")})
    artist_name = tag_artist["data-username"]

    if len(artist_name) == 0:
        raise ValueError( " ERROR: scrap_for_artist_name_from_art_link(): Cannot find artist name in {}".format(tag_artist) )

    return artist_name

def main():
    config_path = r'./config.json'

    download_dir = get_single_variable_from_json_file( config_path, "download_dir" )
    download_mode = get_single_variable_from_json_file( config_path, "download_mode" )

    if download_mode == "profiles":
        print( ' Download Mode: {}'.format(download_mode) )
        url_profile_list = get_single_variable_from_json_file( config_path, "artist_profiles" )
        for each_profile_url in url_profile_list:
            artist_name, url_list = scrap_for_all_art_link_from_profile_link(url_profile=each_profile_url)

            print( ' Removing dups in art links list' )
            url_list = list(dict.fromkeys(url_list))

            print( ' Downloading for artist {}'.format(artist_name) )
            print( ' Downloading to {}'.format(download_dir) )
            for url in url_list:
                image_link, image_title = scrap_for_current_image_link_and_title(url)

                download_image_from_url(url_image=image_link, to_filename_with_no_extension=artist_name+"__"+image_title, to_dir_path=download_dir)
    elif download_mode == "art_links":
        print( ' Download Mode: {}'.format(download_mode) )
        print( ' Downloading to {}'.format(download_dir) )
        url_art_link_list = get_single_variable_from_json_file( config_path, "art_links" )
        
        for each_art_url in url_art_link_list:
            artist_name = scrap_for_artist_name_from_art_link(url_art=each_art_url)
            image_link, image_title = scrap_for_current_image_link_and_title(each_art_url)

            download_image_from_url(url_image=image_link, to_filename_with_no_extension=artist_name+"__"+image_title, to_dir_path=download_dir)
    else:
        print(' Unknown download_mode given: {}'.format(download_mode))

if __name__ == '__main__':
    t_start = datetime.now()
    main()
    t_end = datetime.now()
    print('')
    print(' Time Elapsed: {}'.format( get_duration(t_start, t_end) ))