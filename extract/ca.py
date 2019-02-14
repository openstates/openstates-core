from .common import (
    extractor_for_element_by_xpath
)

def handle_california(data, metadata):
	if metadata["media_type"] == "text/html":
		return extractor_for_element_by_xpath('.//div[@id="bill"] | .//span[@class="Resolution"]')(data, metadata)
	elif metadata["media_type"] == "application/pdf":
		# return extract_simple_pdf(data, metadata)

		# according to James, Calif. publishes bills as both text and HTML
		# so we don't *need* to extract from PDF.
		pass
	else:
		print("unexpected media type in california", metadata["media_type"])
		assert False