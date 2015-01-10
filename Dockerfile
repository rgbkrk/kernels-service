FROM ipython/ipython

ADD . /srv/singlekernel
WORKDIR /srv/singlekernel

CMD python3 singlekernel.py
