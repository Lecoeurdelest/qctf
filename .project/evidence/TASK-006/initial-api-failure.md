# Initial invalid-token smoke failure

After fixing bootstrap, the Docker stack became healthy and all 10 initial
plugin unit tests passed. The live gateway smoke run passed the UI routes,
health, capabilities and missing-token checks, then failed on an invalid token:

```text
PASS /api/qctf/v1/me (401)
<anonymous_script>:1
<!DOCTYPE html>
^
SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

The upstream request hook aborted before the plugin decorator and CTFd's
existing 401 handler rendered HTML. Repair: override standard HTTP error
handlers with JSON in the headless plugin, retaining HTTP status codes.
Added a regression test for a pre-view upstream abort; live invalid-token
checks remain part of the integration smoke suite.
