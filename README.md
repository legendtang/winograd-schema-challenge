# Introduction
A solver trying to cover winograd schema challenge problem.

# Instruction

Install spacy:

```
pip install spacy-nightly
python -m spacy download en_core_web_sm-2.0.0-alpha --direct   # English
```

Please make sure that you have enough permission to install packages. If not, please install in `virtualenv` instead.

Run the program:

```
python main.py
```

It will shows the statistic information at the end of output.

You may also find help by using `-h`:
```
python main.py -h

usage: main.1.py [-h] [-i INPUT] [-f FORCE] [-n NLP]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input dataset: 1 for WSC2016 and 2 for WSC Example
  -f FORCE, --force FORCE
                        Force making decisions on blank
  -n NLP, --nlp NLP    Output NLP properties
```