from .common import extractor_for_elements_by_xpath, extract_line_numbered_pdf, Metadata

# the sample.csv includes only MSWord files for some Delaware laws
# (actually "HCR" resolutions honoring folks)
# in 'real life' we'll want to make sure to feed to this scraper the PDF link,
# rather than the Docx link.
# Docxes are ignored, PDFs will be handled IFF 'HCR' is in the title.


def handle_delaware(data: bytes, metadata: Metadata) -> str:
    if metadata["media_type"] == "text/html" and "HCR" not in metadata["title"]:
        return extractor_for_elements_by_xpath("/html/body/div[2] | /html/body/div[3]")(
            data, metadata
        )
    elif metadata["media_type"] == "application/pdf" and "HCR" not in metadata["title"]:
        # Del., like many states, appears to publish all bills as both text and HTML
        # so we don't *need* to extract from PDF.
        return ""
    elif metadata["media_type"] == "application/pdf" and "HCR" in metadata["title"]:
        # haha, but Delaware does NOT appear to publish concurrent resolutions
        # (honoring people and recognizing the contributions of general aviation, etc.)
        # as HTML. Just PDF and MSWord.
        # so we handle these here and ignore docx (below)
        return extract_line_numbered_pdf(data, metadata)
    else:
        print("unexpected media type in delaware", metadata["media_type"])
        assert False
