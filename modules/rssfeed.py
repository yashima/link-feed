from feedgen.feed import FeedGenerator
from flask import request,url_for
import pytz

def generate_feed(username, links):
	feed = FeedGenerator()
	feed.id("LinkTool-{username}") #todo user secret
	feed.title(f'Latest LinkTool Links by {username}')
	feed.author({'name':username})
	feed.logo(f'{request.url}/static/favicon.png')
	feed.description('Link Tool RSS Feed for {username}')
	feed.link(href=request.url,rel='self') 
	feed.language('en')    

	# Iterate over the links and add them to the feed
	for link in links:
		share_address = url_for('links.permalink',secret_link=link.secret_link,_external=True)
		entry = feed.add_entry()
		entry.id(link.secret_link)
		entry.guid(guid=link.secret_link,permalink=True)
		entry.title(link.title)
		entry.link(href=link.get_address())
		entry.source(share_address)
		entry.summary(link.summary)
		entry.content(f'<b>Comment:</b> {link.comment} <br/> <b>Summary:</b> {link.summary} <br/> <a href="{share_address}">Linktool Link</a>')
		entry.description(link.comment)
		entry.pubDate(pytz.timezone('Europe/Berlin').localize(link.created_at))

		# Add tags as categories (optional)
		for tag in link.tags:
			entry.category(term=tag.name)

	return feed.rss_str(pretty=True)