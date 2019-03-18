# wasabi
Utility functions for use with learningequality/ricecooker

Currently a pre-release version -- significant chance of changes to interface.

# Node Creation

## create_node (add_file)
```create_node(file_class,
             url|filename,
             title,
             description,
             license,
             copyright_holder)``
            
Create nodes for arbitary files without thinking too much about what type they are.
Will determine content node from:
* file_class (e.g. the VideoFile class)
* downloaded mimetype
* file/url extension
* initial bytes of file (i.e. magic numbers)

Optionally set wasabi.add_file.metadata to a dictionary containing license and copyright_holder
as keys to avoid having to set them on every node.

Unsurprisingly, returns a Node.


## create_carousel_node (build_carousel)
`create_carousel_node(urls, **metadata)`
Convert a list of image URLs into a scrollable carousel. Metadata passed as create_node.
Returns a Node

# Transcoding

## transcode_video, transcode_audio (transcode)
`transcode_video(source_filename, target_filename=None)`
Transcode to MP4 or MP3 audio. Returns the new filename.
