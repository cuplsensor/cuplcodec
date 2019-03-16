FROM mmackay/web_base:latest
COPY decoder /urldecoderdist
RUN pip install --find-links=/urldecoderdist urldecoder
