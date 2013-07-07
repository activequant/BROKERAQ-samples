from distutils.core import setup

setup(
    name='BrokerAQ',
    author='ActiveQuant GmbH',
    author_email='info@activequant.com',
    version='0.1',
    url='http://www.brokeraq.com',
    packages=['aq','aq.domainmodel','aq.stream','aq.util'],
    license='GPL3',
    long_description=open('README.txt').read(),
)
