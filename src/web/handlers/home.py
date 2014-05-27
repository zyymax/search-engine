from base import BaseHandler

class HomeHandler(BaseHandler):
	def get(self):
		template_values = {}
		template_values['query'] = self.get_argument('query', '')
		template_values['field'] = self.get_argument('field', 'token_title')
		self.render("main.html", template_values=template_values)