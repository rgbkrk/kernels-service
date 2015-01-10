FROM ipython/ipython

ADD singlekernel.py /srv/

# The exec form causes kernels to restart unless invoked with sh -c
CMD ["sh", "-c", "/srv/singlekernel.py"]
