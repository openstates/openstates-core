# text-extraction

This repo contains a sampling of Open States' bill versions, currently 25 bills per state-session-chamber-mimetype option.  This should be enough to write robust text extraction code.

## Setup

Create a new virtualenv and then install the dependencies via `pip install -r requirements.txt`

We use ``scrapelib`` - it is used for fetching files from HTTP & FTP sites. Other libraries may be required depending on the state you're working on. Please avoid using BeautifulSoup in favor of ``lxml`` for
stability and speed considerations.

Please work on a branch & check in the text/ directory only when you're happy with the results.  This keeps the repo size down & will allow review of the results of extraction as part of the PR.

## Usage

Run ``./demo.py nc`` (replacing nc with whichever state you're interested in working on)

   *The first time this is run this will populate the directory ``raw/nc`` with sample files, should you ever need to regenerate those feel free to erase that directory & it will be recreated on the next run*
   
## Adding States

To add an extraction function for a state, edit ``extract/__init__.py`` and add the state to the ``CONVERSION_FUNCTIONS`` dict.  If your state is relatively standard, use (or add) a standard extractor function from ``extract/common.py``.  

If your state would greatly benefit from a custom implementation, add a file like ``extract/ca.py`` that handles your specific state's edge case.  

All extraction functions must implement the interface ``f(data, metadata)``, where data is the raw bytes of the HTML/PDF/DOC/etc. and metadata is a dictionary which provides basic metadata.  The two keys of interest in the metadata are: 
 
 * ``classification`` - used to distinguish between upper & lower in the case that bill formats differ
 * ``media_type`` - the type of file, e.g. application/pdf
 
Other metadata values should generally not be used to alter behavior.  In particular, refrain from using ``jurisdiction_id`` to alter behavior within a function, prefering different functions where necessary.


## Output Style Guidelines

**How far do we go? Should we strip punctuation? Newlines? Whitespace? Section headings?**

- Try not to be too aggressive with punctuation stripping, search indices/etc. can easily strip it later, but it can be handy if someone decides they want to search for things like "§ 143C-4-8.b"
- Ideally leave newlines as-is since it makes looking at changes a lot nicer for humans and stripping newlines out for final products (search/text comparison/etc.) is trivial. 
- Collapsing spaces/etc. is recommended, but not required.
- Removal of section headers/etc. is fine, but if the only reason you're writing a new function instead of using a common one is to do this, reconsider.

When in doubt, **ask**, you may have encountered something we haven't considered yet and we can discuss the best practice and add it here.

**Should we include bill digests?**

There isn't a need to, but it doesn't hurt if separating the two is difficult.
