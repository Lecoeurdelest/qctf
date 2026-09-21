# Headless CTFd

qctf removes the bundled core, core-deprecated, and admin themes. The product
UI lives in `apps/web`; the qctf_headless plugin rejects CTFd UI routes.

Keep this directory because upstream theme discovery enumerates it. Restoring
server-rendered CTFd pages requires restoring their templates and assets first.
