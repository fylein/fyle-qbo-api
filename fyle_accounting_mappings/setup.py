"""
Project setup file
"""
import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='fyle-accounting-mappings',
    version='0.1.0',
    author='Shwetabh Kumar',
    author_email='shwetabh.kumar@fyle.in',
    description='Django application to store the accounting mappings in a generic manner',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['fyle', 'rest', 'django-rest-framework', 'api', 'python', 'accounting'],
    url='https://github.com/fylein/fyle-accounting-mappings',
    packages=setuptools.find_packages(),
    install_requires=['django>=3.0.2', 'django-rest-framework>=0.1.0'],
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ]
)
