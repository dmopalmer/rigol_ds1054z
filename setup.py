from setuptools import setup

setup(name='rigol_ds1054z',
      version='0.1',
      description='Control program for Rigol DS1054Z oscilloscope',
      url='https://github.com/charkster/rigol_ds1054z',
      author='charkster',
      author_email='',
      license='MIT',
      packages=['rigol_ds1054z'],
      install_requires=["pyvisa", "pyvisa-py", "numpy"]
      )