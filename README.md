# pdf-diff-service

Requires Python 3+.

## Usage
```
# Start the service on port 8000
$ docker run --rm -it -p "8000:8000" ashwanthkumar/pdf-diff-service:latest
$ curl --location --request POST 'localhost:8000/diff/' --form 'prev=@/path/to/prev.pdf' --form 'current=@/path/to/current.pdf' > diff.png
# open diff.png to view the actual diff
```

## Development Setup
```
$ virtualenv --python python3 DENV
$ source DENV/bin/activate
$ pip install -r requirements.txt

# Start the server on localhost:8000/
$ uvicorn main:app --reload --log-level trace
```
