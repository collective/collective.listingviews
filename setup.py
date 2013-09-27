from setuptools import setup, find_packages

version = '1.0beta3'

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

long_description = long_description.replace('See the `doctests for a worked example`_',
                         open('./src/collective/listingviews/tests/listingviews.rst').read())


setup(name='collective.listingviews',
      version=version,
      description="Listing views",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Python TTW',
      author='Pretaweb',
      author_email='support@pretaweb.com',
      url='http://github.com/collective/collective.listingviews',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.z3cform',
#          'plone.app.testing',
#          'plone.directives.form', # older directives
#          'collective.z3cform.chosen'
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
