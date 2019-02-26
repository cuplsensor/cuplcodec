FROM mmackay/web_base:latest
COPY ./urldecoder/dist /urldecoderdist
RUN pip install --find-links=/urldecoderdist urldecoder
