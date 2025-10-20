from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

class Pagination:

	def __init__(self):
		self._page = 1
		self._size = 10
		self._max_size = 100
		self._total_pages = 1
	
	@property
	def page(self):
		return self._page

	@page.setter
	def page(self, value):
		if value is not None and value.isdigit():
			self._page = int(value)
	
	@property
	def total_pages(self):
		return self._total_pages

	@total_pages.setter
	def total_pages(self, value):
		if value is not None and isinstance(value, int):
			self._total_pages = value

	@property
	def size(self):
		return self._size

	@size.setter
	def size(self, value):
		if value is not None and value.isdigit():
			if int(value) > self._max_size:
				self._size = self._max_size
			else:
				self._size = int(value)
	
	def paginate_data(self, data):
		paginator = Paginator(data, self.size)
		self.total_pages = paginator.num_pages

		try:
			data = paginator.page(self.page)
		except PageNotAnInteger:
			data = paginator.page(self.page)
		except EmptyPage:
			self._page = self.total_pages
			data = paginator.page(self.page)
		
		return data
