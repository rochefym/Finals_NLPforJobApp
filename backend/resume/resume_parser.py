#1. Import Libraries
import streamlit as st
import pandas as pd
import base64, random
import time, datetime

#1.2. Import libraries to parse resumes PDFs
from pyresparser import ResumeParser
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter

import io, random
from streamlit_tags import st_tags
from PIL import Image

import nltk
nltk.download('stopwords')