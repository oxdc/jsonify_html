from setuptools import setup

setup(
   name='jsonify_html',
   version='2.0.1-alpha',
   description='Template-based HTML-to-JSON parser.',
   author='oxdc',
   author_email='projaias@outlook.com',
   url='https://github.com/oxdc/jsonify_html',
   packages=[
       'jsonify_html',
       'jsonify_html.cmd',
       'jsonify_html.parser'
   ],
   install_requires=['lxml', 'pytidylib', 'python-dateutil', 'django-htmlmin', 'cssselect', 'pyyaml']
)
