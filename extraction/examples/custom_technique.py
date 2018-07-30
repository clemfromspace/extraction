"""
This file includes an example of a custom Technique tailored around
parsing articles on my blog at lethain.com. Usage is::

    >>> import extraction, requests
    >>> url = "http://lethain.com/digg-v4-architecture-process/"
    >>> techniques = ["extraction.examples.LethainComTechnique"]
    >>> extractor = extraction.Extractor(techniques=techniques)
    >>> extracted = extractor.extract(requests.get(url))
    >>> extracted.title
    blah

This is also an example of returning additional metadata,
in this case it also extracts a date and tags from the page.
"""

from extraction.techniques import Technique
from parsel import Selector


class LethainComTechnique(Technique):
    """
    Extract data from articles on lethain.com, based on articles being structured like so::

        <div class="page">
            <h2><a href="/digg-v4-architecture-process">Digg v4&#39;s Architecture and Development Processes</a></h2>
            <span class="date">08/19/2012</span>
            <span class="tag"><a href="/tags/architecture/">architecture</a><span class="tagcount">(5)</span></span>
            <span class="tag"><a href="/tags/digg/">digg</a><span class="tagcount">(3)</span></span>
            <div class="text">
              <p>A month ago history reset with...</p>
            </div>
        </div>

    Depending on how many sites you're extracting data from, these techniques are either very
    useful or clinically insane. Perhaps both.
    """

    def extract(self, html):
        """Extract data from lethain.com."""

        selector = Selector(html)
        page_div = selector.xpath('//div[@class="page"]')
        text_div = selector.xpath('//div[@class="text"]')

        return {
            'titles': [page_div.xpath('string(.//h2)').extract_first()],
            'dates': [page_div.xpath('.//span[@class="date"]/text()').extract_first()],
            'descriptions': [' '.join(text_div.xpath('string(.//p)').extract())],
            'tags': page_div.xpath('.//span[@class="tag"]/a/text()').extract(),
            'images': text_div.xpath('.//img/@src').extract(),
        }

