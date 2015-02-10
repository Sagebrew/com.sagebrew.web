from django.conf.urls import patterns, include

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
    (r'^help/conversation/', include('help_center.sub_urls.asking')),
    (r'^help/campaigns/', include('help_center.sub_urls.representatives')),
    (r'^help/conversation/', include(
        'help_center.sub_urls.reputation_and_moderation')),
    (r'^help/conversation/', include('help_center.sub_urls.solutions')),
    (r'^help/accounts/', include('help_center.sub_urls.account')),
    (r'^help/security/', include('help_center.sub_urls.security')),
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