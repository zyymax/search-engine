import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header('Server', 'CSMServer/1.1')

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render("404.html", template_values=[])
        elif status_code == 500:
            self.render("500.html", template_values=[])

    def br(self, value):
        return value.replace("\n", "<br>")

    @property
    def host(self):
        return self.request.host
