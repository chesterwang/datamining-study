#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import platform

setup(
    name="dmstudy",
    version="0.1",
    keywords=("dmstudy"),
    description="dmstudy",
    long_description="dmstudy",
    license="Licence",

    url="https://github.com/chesterwang/datamining-study",
    author="chester wang",
    author_email="wangtongpeng@126.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        "fabric",
        "pandas",
        "beautifulsoup4",
        "Scrapy",
        "APScheduler",
        "cssselect",
        "pyaml",
        "face_recognition",
        "dlib",
        "jieba",
        "sklearn",
        "sklearn-pandas",
        "sklearn2pmml",
        "tensorflow-gpu" if (platform.system() == "Linux") else "tensorflow",
        "keras",
        "matplotlib",
        "statsmodels",
        "nltk",
        "gensim",
        "plotly",
        "bokeh",
        "seaborn",
        "pybrain",
        "gym[atari]",
        "opencv-python",
        "rsa",
        "requests",
        "beautifulsoup4",
        "pylint",
        "paramiko",
        "pydotplus",
        "jupyter",
        "snakebite",
        "pyarrow",
        "hdfs",
        "pyspark",
        "Flask",
        "Flask-Mail",
        "celery",
        "redis",
        "Jinja2",
        "MarkupSafe",
        "Werkzeug",
        "amqp",
        "anyjson",
        "argparse",
        "billiard",
        "blinker",
        "itsdangerous",
        "kombu",
        "pytz",
        "xgboost",
        "h5py",
        "torch",
        "happybase",
        "PrettyTable",
    ],

    scripts=[],
    entry_points={
        # 'console_scripts': [
        #     'test = test.help:main'
        # ]
    }
)