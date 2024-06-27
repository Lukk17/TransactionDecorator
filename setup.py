from setuptools import setup, find_packages

setup(
    name='transaction-decorator',  # Adjust if needed
    version='1.0.1',  # Update version as necessary
    description='A utility to decorate transactions.',
    author='Lukk Sarna',
    author_email='luksarna@gmail.com',
    packages=find_packages(),  # Assumes packages are within 'src'
    install_requires=[
        'chardet==5.2.0',
        'pandas==2.1.3',
        'PySide6==6.6.0',
        'PySide6-Addons==6.6.0',
        'PySide6-Essentials==6.6.0',
        'pytest==8.2.2',
    ]
)
