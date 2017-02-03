"""Config file for converting an ipython notebook to an HTML file...
- using the "basic" template (to generate just an HTML fragment, not a full document)
- extracting figures into separate files and referencing them by name (rather than 
    the default behaviour of inlining the image data)
"""
config = get_config()
exp = config.HTMLExporter
exp.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
exp.template_file = 'basic'

# TODO: Would love to do more here, like write a postprocessor to add jekyll template header,
# not clear on the API, and docs aren't very helpful.
