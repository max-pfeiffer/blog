AUTHOR = 'Max Pfeiffer'
SITENAME = 'The Nerdy Tech Blog'
SITEURL = "https://max-pfeiffer.github.io/blog"
THEME = "hyde"

PATH = "content"

TIMEZONE = 'Europe/Zurich'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

SOCIAL = (
    ("github", "https://github.com/max-pfeiffer"),
)

DEFAULT_PAGINATION = 10

# Hyde theme
PROFILE_IMAGE = "avatar.jpeg"
FOOTER_TEXT = "© 2020 Max Pfeiffer"

# SEO Plugin
SEO_REPORT = False
SEO_ENHANCER = True
SEO_ENHANCER_OPEN_GRAPH = True
SEO_ENHANCER_TWITTER_CARDS = True
LOGO = "https://max-pfeiffer.github.io/blog/images/avatar.jpeg"

# Sitemap plugin
SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.5,
        "indexes": 0.5,
        "pages": 0.5
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly"
    }
}
