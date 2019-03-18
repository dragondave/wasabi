""" invoke with 'pytest' """

from wasabi import create_node, add_file
from ricecooker.classes.nodes import AudioNode

def test_create_node_extension():
    node = create_node(filename="fixtures/fake.mp3",
                                license="Public Domain",
                                copyright_holder="X")
    assert isinstance(node, AudioNode)

def test_webm():
    node = create_node(filename="fixtures/bigbuck_webm",
                                license="Public Domain",
                                copyright_holder="X")

def test_mp3():
    node = create_node(filename="fixtures/bigbuck_webm",
                                file_class = add_file.TranscodeAudio,
                                license="Public Domain",
                                copyright_holder="X")

