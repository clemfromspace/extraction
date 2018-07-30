"""This file contains techniques for extracting data from HTML pages."""

from parsel import Selector


class Technique(object):
    def __init__(self, extractor=None, *args, **kwargs):
        """Capture the extractor this technique is running within, if any."""

        self.extractor = extractor
        super(Technique, self).__init__(*args, **kwargs)

    def extract(self, html):
        """Extract data from a string representing an HTML document."""

        return {
            'titles': [],
            'descriptions': [],
            'images': [],
            'urls': [],
        }


class HeadTags(Technique):
    """Extract info from standard HTML metatags like title, for example:

        <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
            <meta name="author" content="Will Larson" />
            <meta name="description" content="Will Larson&#39;s blog about programming and other things." />
            <meta name="keywords" content="Blog Will Larson Programming Life" />
            <link rel="alternate" type="application/rss+xml" title="Page Feed" href="/feeds/" />
            <link rel="canonical" href="http://lethain.com/digg-v4-architecture-process/">
            <title>Digg v4&#39;s Architecture and Development Processes - Irrational Exuberance</title>
        </head>

    This is usually a last-resort, low quality, but reliable parsing mechanism.
    """

    meta_name_map = {
        "description": "descriptions",
        "author": "authors",
    }

    def extract(self, html):
        """Extract data from meta, link and title tags within the head tag."""

        extracted = {}
        selector = Selector(html)
        # extract data from title tag
        title_tag = selector.xpath('//title/text()').extract_first()
        if title_tag:
            extracted['titles'] = [title_tag]

        # extract data from meta tags
        for meta_tag in selector.xpath('//meta'):
            if 'name' in meta_tag.attrib and 'content' in meta_tag.attrib:
                name = meta_tag.attrib['name']
                if name in self.meta_name_map:
                    name_dest = self.meta_name_map[name]
                    if name_dest not in extracted:
                        extracted[name_dest] = []
                    extracted[name_dest].append(meta_tag.attrib['content'])

        # extract data from link tags
        for link_tag in selector.xpath('//link'):
            if 'rel' in link_tag.attrib:
                if ('canonical' in link_tag.attrib['rel'] or link_tag.attrib['rel'] == 'canonical') and 'href' in link_tag.attrib:
                    if 'urls' not in extracted:
                        extracted['urls'] = []
                    extracted['urls'].append(link_tag.attrib['href'])
                elif ('alternate' in link_tag.attrib['rel'] or link_tag.attrib['rel'] == 'alternate') and 'type' in link_tag.attrib and link_tag.attrib['type'] == "application/rss+xml" and 'href' in link_tag.attrib:
                    if 'feeds' not in extracted:
                        extracted['feeds'] = []
                    extracted['feeds'].append(link_tag.attrib['href'])
        return extracted


class FacebookOpengraphTags(Technique):
    """Extract info from html Facebook Opengraph meta tags.

    Facebook tags are ubiquitous on high quality sites, and tend to be higher quality
    than more manual discover techniques. Especially for picking high quality images,
    this is probably your best bet.

    Some example tags from `the Facebook opengraph docs <https://developers.facebook.com/docs/opengraphprotocol/>`::

        <meta property="og:title" content="The Rock"/>
        <meta property="og:type" content="movie"/>
        <meta property="og:url" content="http://www.imdb.com/title/tt0117500/"/>
        <meta property="og:image" content="http://ia.media-imdb.com/rock.jpg"/>
        <meta property="og:site_name" content="IMDb"/>
        <meta property="fb:admins" content="USER_ID"/>
        <meta property="og:description"
            content="A group of U.S. Marines, under command of
                     a renegade general, take over Alcatraz and
                     threaten San Francisco Bay with biological
                     weapons."/>

    There are a bunch of other opengraph tags, but they don't seem
    useful to extraction's intent at this point.
    """

    key_attr = 'property'
    property_map = {
        'og:title': 'titles',
        'og:url': 'urls',
        'og:image': 'images',
        'og:description': 'descriptions',
    }

    def extract(self, html):
        """Extract data from Facebook Opengraph tags."""

        extracted = {}
        selector = Selector(html)
        for meta_tag in selector.xpath('//meta'):
            if self.key_attr in meta_tag.attrib and 'content' in meta_tag.attrib:
                property = meta_tag.attrib[self.key_attr]
                if property in self.property_map:
                    property_dest = self.property_map[property]
                    if property_dest not in extracted:
                        extracted[property_dest] = []
                    extracted[property_dest].append(meta_tag.attrib['content'])

        return extracted


class TwitterSummaryCardTags(FacebookOpengraphTags):
    """Extract info from the Twitter SummaryCard meta tags."""

    key_attr = 'name'
    property_map = {
        'twitter:title': 'titles',
        'twitter:description': 'descriptions',
        'twitter:image': 'images',
    }


class HTML5SemanticTags(Technique):
    """
    The HTML5 `article` tag, and also the `video` tag give us some useful
    hints for extracting page information for the sites which happen to
    utilize these tags.

    This technique will extract information from pages formed like::

        <html>
          <body>
            <h1>This is not a title to HTML5SemanticTags</h1>
            <article>
              <h1>This is a title</h1>
              <p>This is a description.</p>
              <p>This is not a description.</p>
            </article>
            <video>
              <source src="this_is_a_video.mp4">
            </video>
          </body>
        </html>

    Note that `HTML5SemanticTags` is intentionally much more conservative than
    `SemanticTags`, as it provides high quality information in the small number
    of cases where it hits, and otherwise expects `SemanticTags` to run sweep
    behind it for the lower quality, more abundant hits it discovers.
    """

    def extract(self, html):
        """Extract data from HTML5 semantic tags."""

        titles = []
        descriptions = []
        videos = []
        selector = Selector(html)
        for article in selector.xpath('//article') or []:
            title = article.xpath('string(.//h1)').extract()
            print(title)
            if title:
                titles.append(' '.join(title))
            desc = article.xpath('string(.//p)')
            if desc:
                descriptions.append(' '.join(desc.extract()))

        for video in selector.xpath('.//video') or []:
            for source in video.xpath('.//source') or []:
                if 'src' in source.attrib:
                    videos.append(source.attrib['src'])

        return {
            'titles': titles,
            'descriptions': descriptions,
            'videos': videos
        }


class SemanticTags(Technique):
    """
    This technique relies on the basic tags themselves--for example,
    all IMG tags include images, most H1 and H2 tags include titles,
    and P tags often include text usable as descriptions.

    This is a true last resort technique.
    """
    # list to support ordering of semantics, e.g. h1
    # is higher quality than h2 and so on
    # format is ("name of tag", "destination list", store_first_n)
    extract_string = [
        ('string(//h1)', 'titles', 3),
        ('string(//h2)', 'titles', 3),
        ('string(//h3)', 'titles', 1),
        ('string(//p)', 'descriptions', 5),
    ]
    # format is ("name of tag", "destination list", "name of attribute" store_first_n)
    extract_attr = [('//img', 'images', 'src', 10)]

    def extract(self, html):
        """Extract data from usual semantic tags."""

        extracted = {}
        soup = Selector(html)

        for tag, dest, max_to_store in self.extract_string:
            for found in soup.xpath(tag)[:max_to_store] or []:
                if dest not in extracted:
                    extracted[dest] = []
                extracted[dest].append(found.extract())

        for tag, dest, attribute, max_to_store in self.extract_attr:
            for found in soup.xpath(tag)[:max_to_store] or []:
                if attribute in found.attrib:
                    if dest not in extracted:
                        extracted[dest] = []
                    extracted[dest].append(found.attrib[attribute])

        return extracted


