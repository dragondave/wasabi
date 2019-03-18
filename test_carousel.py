from wasabi import create_carousel_node

def test_carousel():
    create_carousel_node(
            ["http://placekitten.com/200/300",
             "http://placekitten.com/200/301",
             "http://placekitten.com/200/302",
             "http://placekitten.com/200/303",
             "http://placekitten.com/200/304"],
            license = "Public Domain",
            copyright_holder = "X")

