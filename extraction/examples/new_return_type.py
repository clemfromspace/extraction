"""Example of extracting and returning address, a non-standard type of extraction."""

from parsel import Selector

from extraction.techniques import Technique
from extraction import Extractor, Extracted


class AddressExtracted(Extracted):
    def __init__(self, addresses=None, *args, **kwargs):
        """Create an extractor which also knows the address datatype."""

        if addresses is None:
            addresses = []

        assert type(addresses) in (list, tuple), "addresses must be a list or tuple"

        self.addresses = addresses
        super(AddressExtracted, self).__init__(*args, **kwargs)

    @property
    def address(self):
        "Return the best address, if any."
        if self.addresses:
            return self.addresses[0]
        else:
            return None


class AddressExtractor(Extractor):
    """Extractor which supports addresses as first-class data."""

    extracted_class = AddressExtracted
    text_types = ["titles", "descriptions", "addresses"]


class AddressTechnique(Technique):
    def extract(self, html):
        """Extract address data from willarson.com."""

        selector = Selector(html)
        div = selector.xpath('string(//div[@id="address"])')

        return {
            'addresses': [" ".join(div.extract())],
        }
