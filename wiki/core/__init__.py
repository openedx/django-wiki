import bleach
import markdown
from bleach.css_sanitizer import CSSSanitizer
from wiki.conf import settings


class ArticleMarkdown(markdown.Markdown):

    def __init__(self, article, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = article

    def convert(self, text, *args, **kwargs):
        html = super().convert(text, *args, **kwargs)
        if settings.MARKDOWN_SANITIZE_HTML:
            css_sanitizer = CSSSanitizer()
            if settings.MARKDOWN_HTML_STYLES:
                css_sanitizer = CSSSanitizer(allowed_css_properties=settings.MARKDOWN_HTML_STYLES)
            html = bleach.clean(
                html,
                tags=settings.MARKDOWN_HTML_WHITELIST,
                attributes=settings.MARKDOWN_HTML_ATTRIBUTES,
                css_sanitizer=css_sanitizer,
                strip=True,
            )
        return html

def article_markdown(text, article, *args, **kwargs):
    md = ArticleMarkdown(article, *args, **kwargs)
    html = md.convert(text)
    return html
