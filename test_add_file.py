""" invoke with 'pytest' """

import add_file
from ricecooker.classes.nodes import AudioNode

def test_create_node_extension():
    node = add_file.create_node(filename="fixtures/fake.mp3",
                                license="Public Domain",
                                copyright_holder="X")
    assert isinstance(node, AudioNode)

def test_webm():
    node = add_file.create_node(filename="fixtures/bigbuck_webm",
                                license="Public Domain",
                                copyright_holder="X")
