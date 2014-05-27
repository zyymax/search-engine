from base import BaseHandler

class AboutHandler(BaseHandler):
    def get(self):
        self.render('about.html', template_values=[])
