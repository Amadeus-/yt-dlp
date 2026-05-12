from .common import InfoExtractor
from ..utils import float_or_none, url_or_none


class IcePornIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?iceporn\.com/(?:embed|video)/(?P<id>[0-9]+)'
    _TESTS = [{
        # Primary test — video with all three quality tiers (lq + hq + 4k).
        # Default `best` selector picks the 4k variant; exercises full
        # format-selection path.
        'url': 'https://www.iceporn.com/video/7232235/big-ass-teen-stepsis-fucks-pervy-stepbro',
        'md5': '5dcbb474004ef291a82abac2c7daa5f4',
        'info_dict': {
            'id': '7232235',
            'ext': 'mp4',
            'title': 'Big ass teen stepsis fucks pervy stepbro',
            'age_limit': 18,
            'duration': 376.742,
            'thumbnail': r're:^https://g\d+\.iceppsn\.com/media/videos/tmb/7232235/preview/\d+\.jpg$',
        },
    }, {
        # Older user upload that exists only at lq (238p). Covers the
        # files.hq == null / files.4k == "" branch of the format loop.
        'url': 'https://www.iceporn.com/embed/1160223',
        'md5': 'eacdaa9e66d3bf14b67f9cb408dbb382',
        'info_dict': {
            'id': '1160223',
            'ext': 'mp4',
            'title': 'Sultry blonde wife with nice tits fucks a stranger in front of her man',
            'age_limit': 18,
            'duration': 2609,
            'thumbnail': r're:^https://g\d+\.iceppsn\.com/media/videos/tmb/1160223/preview/13\.jpg$',
        },
    }, {
        'url': 'https://www.iceporn.com/video/1160223/sultry-blonde-wife-with-nice-tits-fucks-a-stranger-in-front-of-her-man',
        'only_matching': True,
    }]

    # Quality names map to heights per the embed page's player config:
    # quality_titles: {'4k': '2160p', hq: '720p', lq: '320p'}
    _QUALITY_HEIGHT = {
        '4k': 2160,
        'hq': 720,
        'lq': 320,
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        embed_url = f'https://www.iceporn.com/embed/{video_id}'

        # Fetch the embed page first to establish session cookies.
        # Without these cookies the JSON endpoint silently returns `[]`.
        self._download_webpage(embed_url, video_id, note='Downloading embed page')

        data = self._download_json(
            'https://www.iceporn.com/player_config_json/', video_id,
            note='Downloading player config',
            query={
                'vid': video_id,
                'aid': '0',
                'domain_id': '0',
                'embed': '1',
                'ref': 'null',
                'check_speed': '0',
            },
            headers={
                'Referer': embed_url,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
            })

        formats = []
        for quality, file_url in (data.get('files') or {}).items():
            if not file_url:
                continue
            formats.append({
                'url': file_url,
                'format_id': quality,
                'height': self._QUALITY_HEIGHT.get(quality),
                'http_headers': {'Referer': embed_url},
                # iceporn throttles each signed URL server-side (the `speed=NN`
                # query param). On long videos that means 30+ minute downloads —
                # use chunked HTTP so a connection blip mid-download only loses
                # the current 10 MB chunk instead of restarting from zero.
                'downloader_options': {
                    'http_chunk_size': 10485760,  # 10 MB
                },
            })

        return {
            'id': video_id,
            'title': data.get('title') or video_id,
            'formats': formats,
            'age_limit': 18,
            'duration': float_or_none(data.get('duration')),
            'thumbnail': url_or_none(data.get('poster')),
        }
