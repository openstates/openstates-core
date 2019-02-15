from .common import (
    extractor_for_element_by_xpath
)

def handle_hawaii(data, metadata):
    if metadata["media_type"] == "text/html":
        return extractor_for_element_by_xpath('.//*[@class="Section2"] | .//*[@class="WordSection2"]')(data, metadata)
    elif metadata["media_type"] == "application/pdf":
        # seems like hawaii publishes bills as both text and HTML
        # so we don't *need* to extract from PDF.
        pass
    else:
        print("unexpected media type in hawaii", metadata["media_type"])
        assert False