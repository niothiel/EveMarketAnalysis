from jinja2 import Markup

class momentjs:
	def __init__(self, timestamp):
		self.timestamp = timestamp

	def render(self, format):
		return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

	def format(self, fmt):
		return self.render("format(\"%s\")" % fmt)

	def calendar(self):
		return self.render("calendar()")

	def fromNow(self):
		return self.render("fromNow()")

	# TODO: Fix this. Even though the code is right, the templating engine comes back with a "class instance has no
	# instance named '__call__', maybe it was the change over to new versions?
	def __call__(self, *args, **kwargs):
		return momentjs(args[0])