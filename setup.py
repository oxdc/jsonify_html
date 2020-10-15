from setuptools import setup

setup(
   name='jsonify_html',
   version='0.1.9',
   description='Template-based HTML-to-JSON parser.',
   author='oxdc',
   author_email='projaias@outlook.com',
   url='https://github.com/oxdc/jsonify_html',
   packages=[
       'jsonify_html',
       'jsonify_html.cmd',
       'jsonify_html.cmd.implementations'
   ],
   install_requires=['lxml', 'python-dateutil', 'django-htmlmin']
)
