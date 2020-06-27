Give some profile link on deviant art, and it will auto download the highest quality image of all its public downloadable images.

Meant to be downloaded into one folder, and have a program cycle through the directory and periodically change the wall paper with one random one in the directory

config.json sample:
```
{
    "download_dir": "/path/to/where/you/want/to/download/to",
    "artist_profiles":
    [
        "https://www.deviantart.com/arsenixc",
        "https://www.deviantart.com/looknamtcn",
        "https://www.deviantart.com/razaras"
    ],
    "art_links":
    [
        "https://www.deviantart.com/arsenixc/art/Wentmon-845001018",
        "https://www.deviantart.com/arsenixc/art/Modern-Metropolis-805751699",
        "https://www.deviantart.com/arsenixc/art/Romantic-city-803896209"
    ],
    "download_mode": "profiles"
}
```
Acceptable value for download_mode is "profiles" or "art_links", this will allow you to download ALL the public image of a artist's profile. Or download from specified links only.

Dependencies (Python libraries):
* Python 3.8.2 (Earlier versions may work, but not tested)
* requests
* bs4
* re
* tqdm
* math
* json

usage:
* Create 'config.json' with the sample config.json above, and fill out the correct configs
* Make sure the DeviantArtScrap.py and config.json are in the same dir
* Then run
```
python ./DeviantArtScrap.py
```