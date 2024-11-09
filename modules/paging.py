import math
from flask import request

items_per_page=20
visible_pages=2


def get_paging_info(item_count):
	current_page = int(request.args.get('page', 1))
	total = math.ceil(item_count / items_per_page)
	start = max(current_page - visible_pages, 1)
	end = min(current_page + visible_pages, total)
	return {'start': start, 'end': end, 'count': item_count, 'total': total, 'page': current_page}
