# single-jupyter-kernel

Launch a single Jupyter kernel over HTTP. Provides only the kernel API of IPython.

### Direct launch

singlekernel.py starts a tornado web server that launches a kernel

Here we set the base path of the IPython API to start at `/minipython/`:

```
$ python singlekernel.py --base-path=minipython
[I 150110 01:03:41 singlekernel:107] Serving at http://127.0.0.1:8000/minipython/api/kernels/1
[I 150110 01:03:52 web:1811] 200 GET /minipython/api/kernels/1 (127.0.0.1) 29.22ms
```

A Docker image is available for launching directly:

```
$ docker run -it -p 8000:8000 rgbkrk/single-jupyter-kernel
```

Several environment variables are available for configuration:

-----------------------------------------------------------------------------------------------------------
KERNEL_ID   | The one kernel ID to launch with, defaults to '1'
-----------------------------------------------------------------------------------------------------------
KERNEL_NAME | The name of the kernel (language type) to use, defaults to system python (could be 'ir' e.g.)
-----------------------------------------------------------------------------------------------------------

Derivative images of `rgbkrk/single-jupyter-kernel` that install kernels like IJulia or the IRKernel need only define these in their Dockerfiles.
