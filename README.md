# kernels-service

Launch Jupyter kernels over HTTP. Provides only the kernels and kernelspecs APIs of IPython/Jupyter.

### Direct launch

kernels.py starts a tornado web server that launches a single kernel and provides the ability to launch more.

Here we set the base path of the IPython API to start at `/jupyter/`:


```console
$ python kernels.py --base-path=jupyter
[I 150113 14:32:13 kernelmanager:85] Kernel started: a8064a6c-a5a4-45d3-8d50-b226efc10f65
[I 150113 14:32:13 kernels:89] Serving at http://127.0.0.1:8000/jupyter/api/kernels
^C[I 150113 14:32:15 kernels:93] Interrupted...
[I 150113 14:32:16 multikernelmanager:140] Kernel shutdown: a8064a6c-a5a4-45d3-8d50-b226efc10f65
```

A Docker image is available for launching directly:

```
$ docker run -it -p 8000:8000 rgbkrk/kernels
```

Several environment variables are available for configuration:

Environment Variable | Description
---------------------|----------------------------------------------------------------------------------------------------------
`KERNEL_NAME`        | The name of the initial kernel (language type) to use, defaults to system python (could be 'ir' for the R Kernel)

Derivative images of `rgbkrk/kernels` that install kernels like IJulia or the IRKernel need only define these in their Dockerfiles. :warning: Depending on your usage, you may want to include a non-root user in the Docker image that runs the service itself. :warning:

Options for base path and port are provided via command line arguments (like the tmpnb demo image). If used directly, they must be done with `sh -c` explicitly:

```console
$ docker run -it -p 8000:8000 rgbkrk/kernels sh -c "/srv/kernels.py --base-path=/krn/"
[I 150113 10:43:00 kernelmanager:85] Kernel started: 83de760b-51d3-420b-a05b-2467439ac45c
[I 150113 10:43:00 kernels:89] Serving at http://127.0.0.1:8000/krn/api/kernels
```

Otherwise you get that awkward kernel restart that occurs when IPython and Docker's pseudo-exec collide:

```console
$ docker run -it -p 8000:8000 rgbkrk/kernels /srv/kernels.py --base-path=/krn/
[I 150113 10:43:49 kernelmanager:85] Kernel started: c8c3fa7c-3b5b-47f9-b863-cb59cc26ea26
[I 150113 10:43:49 kernels:89] Serving at http://127.0.0.1:8000/krn/api/kernels
[I 150113 10:43:52 restarter:103] KernelRestarter: restarting kernel (1/5)
...
```

### Connecting to the kernel over JavaScript

This is terribly hacky, there must be a better way. I'm directly using one notebook to get access to the kernel running *somewhere* else.

```JavaScript
// Hokey creation of a kernel object
var k = new IPython.Kernel("", "", IPython.notebook);

// This kernel can be located anywhere
k.ws_url = 'ws://127.0.0.1:8000'

// Using the full path provided on launch
k.kernel_url = "/krn/api/kernels/5b7ad625-4484-403a-a7c3-8b16394b2ae7"
k.kernel_id = "5b7ad625-4484-403a-a7c3-8b16394b2ae7"

k.start_channels()

// TODO: Wait for the websocket connection to finalize
k.execute('import os; os.mkdir("touchdown")');
```

In reality, I want to be able to use the kernel *without* a notebook.

The reason is that events are propagated to a notebook model in the JavaScript.
