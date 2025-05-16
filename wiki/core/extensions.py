from markdown.extensions import Extension

from wiki.core.processors import AnchorTagProcessor


class AnchorTagExtension(Extension):
    """
    Custom extension to register anchor tag processor with Markdown.
    """
    def extendMarkdown(self, md):
        md.treeprocessors.register(AnchorTagProcessor(md), 'AnchorTagProcessor', 20)
