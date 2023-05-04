import scrapy
import re
from datetime import datetime
from markdownify import markdownify

class SitemapSpeeder(scrapy.spiders.SitemapSpider):
    """
    A spider that extracts data from a sitemap.
    """

    name = 'sitemap'
    sitemap_urls = ['https://dfoarchive.blogspot.com/sitemap.xml']
    sitemap_rules = [
        ('https://dfoarchive.blogspot.com/*', 'parse')
    ]

    def parse(self, response):
        """
        Parse the sitemap and extract blog data and metadata.

        Args:
            response (scrapy.http.Response): The response received from the sitemap.

        Yields:
            dict: A dictionary containing the extracted blog data and metadata.
        """

        # Extract post body HTML
        post_body_html = response.css('div.post-body').get()

        # Convert post body HTML to markdown and remove formatting, images, and links
        md_body = markdownify(post_body_html, strip=['b', 'i', 'img', 'a'])

        # Extract latest date metadata from the post header
        post_header_html = response.css('div.post-header').get()
        md_header = markdownify(post_header_html)

        # Define regular expressions for date patterns
        date_1_pat = r"Published On:\s*(\w+,\s+\w+\s+\d{1,2},\s+\d{4})"
        date_2_pat = r'(\d{4}-\d{2}-\d{2})'

        # Search for date matches in the post header markdown
        date_1_match = re.search(date_1_pat, md_header)
        date_2_match = re.search(date_2_pat, md_header)

        # If both date patterns are found in the post header markdown, extract and compare the dates
        if date_1_match and date_2_match:
            date_1 = date_1_match.group(1)
            date_1 = datetime.strptime(date_1, '%A, %B %d, %Y')
            date_2 = date_2_match.group(1)
            date_2 = datetime.strptime(date_2, '%Y-%m-%d')
            if date_1 > date_2:
                latest_date = date_1
            else:
                latest_date = date_2

        # If only date pattern 1 is found, extract the date
        elif date_1_match:
            date_1 = date_1_match.group(1)
            date_1 = datetime.strptime(date_1, '%A, %B %d, %Y')
            latest_date = date_1

        # If only date pattern 2 is found, extract the date
        elif date_2_match:
            date_2 = date_2_match.group(1)
            date_2 = datetime.strptime(date_2, '%Y-%m-%d')
            latest_date = date_2

        # Format the latest date as a string in YYYY-MM-DD format
        latest_date = latest_date.strftime('%Y-%m-%d')

        # Yield the extracted data and metadata
        yield {
            'blog': md_body,
            'metadata': {'date': latest_date}
        }
