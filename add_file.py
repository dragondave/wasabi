import requests

from ricecooker.classes.nodes import DocumentNode, VideoNode, TopicNode, AudioNode, HTML5AppNode
from ricecooker.classes.files import HTMLZipFile, VideoFile, SubtitleFile, DownloadFile, AudioFile, DocumentFile, ThumbnailFile, WebVideoFile, Base64ImageFile, YouTubeSubtitleFile, YouTubeVideoFile
from le_utils.constants import licenses

from urllib.parse import urlsplit
import hashlib
import os

class UnidentifiedFileType(Exception):
    pass

DOWNLOAD_FOLDER = "__downloads"  # this generates completed files
metadata = {}

try:
    os.mkdir(DOWNLOAD_FOLDER)
except FileExistsError:
    pass


node_dict = {VideoFile: VideoNode,
             AudioFile: AudioNode,
             HTMLZipFile: HTML5AppNode,
             DocumentFile: DocumentNode}

# Long-Range TODOs
# -- detect and re-encode non-MP4 videos, non-MP3 audio, etc.
# -- package up images as zip files (using build_carousel)

def guess_extension(url):
    "Return the extension of a URL, i.e. the bit after the ."
    if not url:
        return ""
    filename = urlsplit(url).path
    if "." not in filename[-8:]: # arbitarily chosen
        return ""
    ext = "." + filename.split(".")[-1].lower()
    if "/" in ext:  # dot isn't in last part of path
        return ""
    return ext

def create_filename(url):
    return hashlib.sha1(url.encode('utf-8')).hexdigest() + guess_extension(url)

def download_file(url):
    """
    Download file to the DOWNLOAD_FOLDER with a content-generated filename.
    Return that filename and the mime type the server told us the file was
    """

    # url must be fully specified!
    response = requests.get(url, stream=True)
    filename = DOWNLOAD_FOLDER + "/" + create_filename(url)
    if not os.path.exists(filename):
        print ("Downloading to {}".format(filename))
        print ("{} bytes".format(response.headers.get("content-length")))
        try:
            with open(filename, "wb") as f:
                # https://www.reddit.com/r/learnpython/comments/27ba7t/requests_library_doesnt_download_directly_to_disk/
                for chunk in response.iter_content( chunk_size = 1024 ):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
        except:  # Explicitly, we also want to catch CTRL-C here.
            print("Catching & deleting bad zip created by quitting")
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
            raise

            print ("{} bytes written".format(response.headers.get("content-length")))
    else:
        print ("Already exists in cache")
    return filename, response.headers.get("content-type")

def create_node(file_class=None, url=None, filename=None, title=None, license=None, copyright_holder=None, description=""):
    """
    Create a content node from either a URL or filename.
    Which content node is determined by:
    * the 'file_class' explicitly passed (e.g. VideoFile)
    * guessing from downloaded mimetype, file extension or magic bytes
    (see guess_type function)

    Use metadata to automatically fille in licence and copyright_holder details --
    if they're not provided correctly, things will break downstream
    """

    mime = None
    if filename is None:
        assert url, "Neither URL nor filename provided to create_node"
        filename, mime = download_file(url)

    if file_class is None:
        with open(filename, "rb") as f:
            magic_bytes = f.read(8)[:8]  # increase if we use python_magic
        file_class = guess_type(mime_type=mime,
                                extension=guess_extension(url or filename),
                                magic=magic_bytes)
        # there is a reasonable chance that the file isn't actually a suitable filetype
        # and that guess_type will raise an UnidentifiedFileType error.
    assert file_class

    # Ensure file has correct extension for the type of file we think it is:
    # this is a requirement from sushichef.
    extensions = {VideoFile: ".mp4",
                  AudioFile: ".mp3",
                  DocumentFile: ".pdf",
                  HTMLZipFile: ".zip",}
    extension = extensions[file_class]
    if not filename.endswith(extension):
        new_filename = filename + extension
        os.rename(filename, new_filename)
        filename = new_filename

    # print (filename, os.path.getsize(filename))

    # Do not permit zero-byte files
    assert(os.path.getsize(filename))

    kwargs = {VideoFile: {"ffmpeg_settings": {"max_width": 480, "crf": 28}},
              AudioFile: {},
              DocumentFile: {},
              HTMLZipFile: {}}
    file_instance = file_class(filename, **kwargs[file_class])

    node_class = node_dict[file_class]

    return node_class(source_id=filename,  # unique due to content-hash
                      title=title,
                      license=license or metadata['license'],
                      copyright_holder=copyright_holder or metadata['copyright_holder'],
                      files=[file_instance],
                      description=description,
                      )

def guess_type(mime_type="",
               extension="",
               magic=b""):

    content_mapping = {"audio/mp3": AudioFile,
                       "video/mp4": VideoFile,
                       "audio/mp4": VideoFile,
                       "application/pdf": DocumentFile,
                       }

    if mime_type in content_mapping:
        return content_mapping[mime_type]

    extension_mapping = {".mp3": AudioFile,
                         ".mp4": VideoFile,
                         ".pdf": DocumentFile,
                         # m4v!
                         # "zip": HTMLZipFile,  # primarily for carousels
                         }

    if extension in extension_mapping:
        return extension_mapping[extension]

    magic_mapping = {b"\xFF\xFB": AudioFile,
                     b"ID3": AudioFile,
                     b"%PDF": DocumentFile,
                     # b"PK": HTMLZipFile,
                     }

    for mapping in magic_mapping:
        if magic.startswith(mapping):
            return magic_mapping[mapping]

    # TODO -- consider using python_magic library

    raise UnidentifiedFileType(str([mime_type, extension]))

def get_type_and_response(url):
    """Guess the type of a URL and preserve the response to avoid downloading twice"""
    response = requests.get(url)
    response.raise_for_status()
    # get the bit before the semi-colon -- should be audio/mp3 or similar
    content_type = response.headers.get('Content-Type', "").split(";")[0].strip()
    extension = guess_extension(response.url)
    magic = response.content[:4]
    try:
        file_type = guess_type(content_type, extension, magic)
    except UnidentifiedFileType:
        file_type = None
    return [file_type, response]

def guess_by_url(url):
    return get_type_and_response(url)[0]

if __name__ == "__main__":
    print(create_node(DocumentFile, "http://www.pdf995.com/samples/pdf.pdf", license=licenses.CC_BY_NC_ND, copyright_holder="foo"))
