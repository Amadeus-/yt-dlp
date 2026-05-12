from .common import InfoExtractor


class ColliderPornIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?colliderporn\.com/en/look/(?P<id>[0-9]+)/[^/?#]+\.php'
    _TESTS = [{
        'url': 'https://colliderporn.com/en/look/31299411/cuckold.php',
        'md5': 'eacdaa9e66d3bf14b67f9cb408dbb382',
        'info_dict': {
            'id': '1160223',
            'ext': 'mp4',
            'title': 'Cuckold - Collider Porn',
            'age_limit': 18,
            'duration': 2609,
            'thumbnail': r're:^https://g\d+\.iceppsn\.com/media/videos/tmb/1160223/preview/13\.jpg$',
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = (
            self._og_search_title(webpage, default=None)
            or self._html_extract_title(webpage, fatal=True)
        )

        iframe_url = self._search_regex(
            r'''window\.location\.replace\(['"]([^'"]+)['"]\)''',
            webpage, 'iframe URL')

        return {
            '_type': 'url_transparent',
            'url': iframe_url,
            'id': video_id,
            'title': title,
            'age_limit': 18,
            'description': self._og_search_description(webpage, default=None),
        }
