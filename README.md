# SpiderTools

Create a python wrapper around the following SpiderLab tools:

- [x] [Tacoco](https://github.com/spideruci/tacoco)
- [ ] [Blinky-Core](https://github.com/spideruci/blinky-core)

The goal is to allow us to write experiments in Python without having to relearn how each tool exactly works.

## Install
- The SpiderTools can be installed using the following commands:
```
git clone https://github.com/kajdreef/spidertools
cd spidertools
pip3 install -e .
```

## Development
- Dependencies:
    - Python3.8
    - tox
    - [optional/recommended] virtualenv

- Running Tests: `tox`

To make use of the wrappers the tools itself need to be installed as well, see the documentation for each project how to do that.

## TODO: 
- [ ] History slicing
- [ ] Add [Blinky](https://github.com/spideruci/blinky-core) support in combination with tacoco
- [ ] Store intermediate results in a tmp directory and remove that tmp directory after the analysis is done.
- [ ] Sanitize request input on the server. Currently, it grabs input and passes it directly to the database. Easy to do SQL injection.
- [ ] Create sorting endpoint, that allows to post data and sort.
    - [ ] sorting based on name
    - [ ] Agglomerative clustering based on name
    - [ ] Agglomerative clustering based on what is tested
- [ ] Create filter endpoint, that allows me to post data and filter.
- [ ] fix:
```
[ERROR] test_name error: [4] UnsynchronizedByteArrayOutputStream.toBufferedInputStream(InputStream, int).[engine:junit-jupiter]/[class:org.apache.commons.io.output.ByteArrayOutputStreamTestCase]/[test-template:testToBufferedInputStreamEmpty(java.lang.String, org.apache.commons.io.function.IOFunction)]/[test-template-invocation:#4]
[ERROR] test_name error: [1] ByteArrayOutputStream.[engine:junit-jupiter]/[class:org.apache.commons.io.output.ByteArrayOutputStreamTestCase]/[test-template:testStream(java.lang.String, org.apache.commons.io.output.ByteArrayOutputStreamTestCase$BAOSFactory)]/[test-template-invocation:#1]
```