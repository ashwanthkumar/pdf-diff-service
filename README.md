# pdf-diff-service

## Running it Locally
```
$ virtualenv --python python3 DENV
$ source DENV/bin/activate
$ pip install -r requirements.txt

# Start the server on localhost:8000/
$ uvicorn main:app --reload --log-level trace
```

## Testing it Locally
```
curl --location --request POST 'localhost:8000/diff/' \
--form 'prev=@/path/to/prev.pdf' \
--form 'current=@/path/to/current.pdf'
```
