import logging

from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save, pre_delete
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from wiki import managers
from wiki.conf import settings
from wiki.core.exceptions import MultipleRootURLs, NoRootURL
from wiki.middleware import get_current_request
from wiki.models.article import Article, ArticleForObject, ArticleRevision

log = logging.getLogger(__name__)

class URLPath(MPTTModel):
    """
    Strategy: Very few fields go here, as most has to be managed through an
    article's revision. As a side-effect, the URL resolution remains slim and swift.

    .. no_pii:
    """
    # Tells django-wiki that permissions from a this object's article
    # should be inherited to children's articles. In this case, it's a static
    # property.. but you can also use a BooleanField.
    INHERIT_PERMISSIONS = True

    objects = managers.URLPathManager()

    articles = fields.GenericRelation(ArticleForObject)

    # Do NOT modify this field - it is updated with signals whenever ArticleForObject is changed.
    article = models.ForeignKey(Article, on_delete=models.CASCADE, editable=False,
                                verbose_name=_('Cache lookup value for articles'))

    # The slug is constructed from course key and will in practice be much shorter then 255 characters
    # since course keys are capped at 65 characters in the Studio (https://openedx.atlassian.net/browse/TNL-889).
    SLUG_MAX_LENGTH = 255

    slug = models.SlugField(verbose_name=_('slug'), null=True, blank=True,
                            max_length=SLUG_MAX_LENGTH)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        pass
        # Fixed in django-mptt 0.5.3
        #self._tree_manager = URLPath.objects
        return super().__init__(*args, **kwargs)

    @property
    def cached_ancestors(self):
        """
        This returns the ancestors of this urlpath. These ancestors are hopefully
        cached from the article path lookup. Accessing a foreign key included in
        add_selecte_related on one of these ancestors will not occur an additional
        sql query, as they were retrieved with a select_related.

        If the cached ancestors were not set explicitly, they will be retrieved from
        the database.
        """
        if not hasattr(self, "_cached_ancestors"):
            self._cached_ancestors = list(self.get_ancestors().select_related_common() )

        return self._cached_ancestors

    @cached_ancestors.setter
    def cached_ancestors(self, ancestors):
        self._cached_ancestors = ancestors

    def set_cached_ancestors_from_parent(self, parent):
        self.cached_ancestors = parent.cached_ancestors + [parent]

    @property
    def path(self):
        if not self.parent: return ""

        ancestors = [ancestor for ancestor in self.cached_ancestors if ancestor.parent is not None]
        slugs = [obj.slug if obj.slug else "" for obj in ancestors + [self] ]

        return "/".join(slugs) + "/"

    def is_deleted(self):
        """
        Returns True if this article or any of its ancestors have been deleted
        """
        return self.first_deleted_ancestor() is not None

    def first_deleted_ancestor(self):
        for ancestor in self.cached_ancestors + [self]:
            if ancestor.article.current_revision.deleted == True:
                return ancestor
        return None

    def delete_subtree(self):
        """
        NB! This deletes this urlpath, its children, and ALL of the related
        articles. This is a purged delete and CANNOT be undone.
        """
        try:
            with transaction.atomic():
                for descendant in self.get_descendants(include_self=True).order_by("-level"):
                    print("deleting " , descendant)
                    descendant.article.delete()
        except:
            log.exception("Exception deleting article subtree.")



    @classmethod
    def root(cls):
        site = get_current_site(get_current_request())
        root_nodes = list(
            cls.objects.root_nodes().filter(site=site).select_related_common()
        )
        # We fetch the nodes as a list and use len(), not count() because we need
        # to get the result out anyway. This only takes one sql query
        no_paths = len(root_nodes)
        if no_paths == 0:
            raise NoRootURL("You need to create a root article on site '%s'" % site)
        if no_paths > 1:
            raise MultipleRootURLs("Somehow you have multiple roots on %s" % site)
        return root_nodes[0]

    class MPTTMeta:
        pass

    def __unicode__(self):
        path = self.path
        return path if path else gettext("(root)")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        assert not (self.parent and self.get_children()), "You cannot delete a root article with children."
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('URL path')
        verbose_name_plural = _('URL paths')
        unique_together = ('site', 'parent', 'slug')

    def clean(self, *args, **kwargs):
        if self.slug and not self.parent:
            raise ValidationError(_('Sorry but you cannot have a root article with a slug.'))
        if not self.slug and self.parent:
            raise ValidationError(_('A non-root note must always have a slug.'))
        if not self.parent:
            if URLPath.objects.root_nodes().filter(site=self.site).exclude(id=self.id):
                raise ValidationError(_('There is already a root node on %s') % self.site)
        super().clean(*args, **kwargs)

    @classmethod
    def get_by_path(cls, path, select_related=False):
        """
        Strategy: Don't handle all kinds of weird cases. Be strict.
        Accepts paths both starting with and without '/'
        """

        # TODO: Save paths directly in the model for constant time lookups?

        # Or: Save the parents in a lazy property because the parents are
        # always fetched anyways so it's fine to fetch them here.
        path = path.lstrip("/")
        path = path.rstrip("/")

        # Root page requested
        if not path:
            return cls.root()

        slugs = path.split('/')
        level = 1
        parent = cls.root()
        for slug in slugs:
            if settings.URL_CASE_SENSITIVE:
                child = parent.get_children().select_related_common().get(slug=slug)
                child.cached_ancestors = parent.cached_ancestors + [parent]
                parent = child
            else:
                child = parent.get_children().select_related_common().get(slug__iexact=slug)
                child.cached_ancestors = parent.cached_ancestors + [parent]
                parent = child
            level += 1

        return parent

    def get_absolute_url(self):
        return reverse('wiki:get', kwargs={'path': self.path})

    @classmethod
    def create_root(cls, site=None, title="Root", request=None, **kwargs):
        if not site: site = get_current_site(get_current_request())
        root_nodes = cls.objects.root_nodes().filter(site=site)
        if not root_nodes:
            # (get_or_create does not work for MPTT models??)
            article = Article()
            revision = ArticleRevision(title=title, **kwargs)
            if request: revision.set_from_request(request)
            article.add_revision(revision, save=True)
            article.save()
            root = cls.objects.create(site=site, article=article)
            article.add_object_relation(root)
        else:
            root = root_nodes[0]
        return root

    @classmethod
    def create_article(cls, parent, slug, site=None, title="Root", article_kwargs={}, **kwargs):
        """Utility function:
        Create a new urlpath with an article and a new revision for the article"""
        if not site: site = get_current_site(get_current_request())
        article = Article(**article_kwargs)
        article.add_revision(ArticleRevision(title=title, **kwargs),
                             save=True)
        article.save()
        newpath = cls.objects.create(site=site, parent=parent, slug=slug, article=article)
        article.add_object_relation(newpath)
        return newpath


######################################################
# SIGNAL HANDLERS
######################################################

# Just get this once
urlpath_content_type = None

def on_article_relation_save(instance, *args, **kwargs):
    global urlpath_content_type
    if not urlpath_content_type:
        urlpath_content_type = ContentType.objects.get_for_model(URLPath)
    if instance.content_type == urlpath_content_type:
        URLPath.objects.filter(id=instance.object_id).update(article=instance.article)

post_save.connect(on_article_relation_save, ArticleForObject)

# TODO: When a parent all of its children are purged, they get
# sucked up into the lost and found. It is disabled for now.
def on_article_delete(instance, *args, **kwargs):
    # If an article is deleted, then throw out its URLPaths
    # But move all descendants to a lost-and-found node.
    site = get_current_site(get_current_request())

    # Get the Lost-and-found path or create a new one
    try:
        lost_and_found = URLPath.objects.get(slug=settings.LOST_AND_FOUND_SLUG,
                                             parent=URLPath.root(),
                                             site=site)
    except URLPath.DoesNotExist:
        article = Article(group_read = True,
                          group_write = False,
                          other_read = False,
                          other_write = False)
        article.add_revision(ArticleRevision(
                 content=_('Articles who lost their parents\n'
                            '===============================\n\n'
                            'The children of this article have had their parents deleted. You should probably find a new home for them.'),
                 title=_("Lost and found")))
        lost_and_found = URLPath.objects.create(slug=settings.LOST_AND_FOUND_SLUG,
                                                parent=URLPath.root(),
                                                site=site,
                                                article=article)
        article.add_object_relation(lost_and_found)


    for urlpath in URLPath.objects.filter(articles__article=instance, site=site):
        # Delete the children
        for child in urlpath.get_children():
            child.move_to(lost_and_found)
        # ...and finally delete the path itself
        # TODO: This should be unnecessary because of URLPath.article(...ondelete=models.CASCADE)
        urlpath.delete()

# pre_delete.connect(on_article_delete, Article)
