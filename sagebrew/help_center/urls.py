from django.conf.urls import patterns, include, url
from .views import related_articles, help_area
'''
content_path is used in sync with the ssi tag in help_page.html to include
the rendered html files from S3. Using python's
http://pythonhosted.org//Markdown/cli.html we can convert the md files into
html in the static folder and then run these right out of the template. This
allows for us to still have a side bar, nav bar, and footer with user centric
material displayed while manging our docs in a markdown format making it easy
for our content creators to manage the information.

'''
urlpatterns = patterns(
    'help_center.views',
    (r'^questions/', include('help_center.sub_urls.questions')),
    (r'^solutions/', include('help_center.sub_urls.solutions')),
    (r'^reputation_and_moderation/', include(
        'help_center.sub_urls.reputation_and_moderation')),
    (r'^conversation/', include('help_center.sub_urls.conversation')),
    (r'^privileges/', include('help_center.sub_urls.privileges')),
    (r'^donating/', include('help_center.sub_urls.donations')),
    (r'^quest/', include('help_center.sub_urls.quest')),
    (r'^reputation/', include(
        'help_center.sub_urls.reputation_and_moderation')),
    (r'^accounts/', include('help_center.sub_urls.account')),
    (r'^security/', include('help_center.sub_urls.security')),
    (r'^terms/', include('help_center.sub_urls.terms')),
    (r'^policies/', include('help_center.sub_urls.policies')),
    url(r'^related_articles/$', related_articles, name="related_articles"),
    url(r'^$', help_area, name="help_center")
)

"""
TODO: We need to ensure we do the following to allow indexing and easier search
Title: My super title
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Category: Python
Tags: pelican, publishing
Slug: my-super-post
Authors: Alexis Metaireau, Conan Doyle
Summary: Short version for index and feeds

See http://docs.getpelican.com/en/3.5.0/content.html#file-metadata for html
metadata result
"""
