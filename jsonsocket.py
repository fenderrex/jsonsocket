import json

## Usage $ twistd -y webserver.py
from pprint import pprint
from twisted.application.internet import TCPServer
from twisted.application.service import Application
from twisted.web.resource import Resource
from twisted.web.server import Site


class Server(Resource):
    def render_GET(self, request):
        return ''

    def render_POST(self, request):
        pprint(request.__dict__)
        newdata = request.content.getvalue()
        print newdata
        return ''
root = Resource()
root.putChild("server", Server())
application = Application("My Web Service")
TCPServer(8880, Site(root)).setServiceParent(application)


class Client(object):
  """
  A JSON socket client used to communicate with a JSON socket server. All the
  data is serialized in JSON. How to use it:

  data = {
    'name': 'Patrick Jane',
    'age': 45,
    'children': ['Susie', 'Mike', 'Philip']
  }
  client = Client()
  client.connect(host, port)
  client.send(data)
  response = client.recv()
  # or in one line:
  response = Client().connect(host, port).send(data).recv()
  """

  socket = None

  def __del__(self):
    self.close()

  def connect(self, host, port):
    self.socket = socket.socket()
    self.socket.connect((host, port))
    return self

  def send(self, data):
    if not self.socket:
      raise Exception('You have to connect first before sending data')
    _send(self.socket, data)
    return self

  def recv(self):
    if not self.socket:
      raise Exception('You have to connect first before receiving data')
    return _recv(self.socket)

  def recv_and_close(self):
    data = self.recv()
    self.close()
    return data

  def close(self):
    if self.socket:
      self.socket.close()
      self.socket = None


## helper functions ##

def _send(socket, data):
  try:
    serialized = json.dumps(data)
  except (TypeError, ValueError), e:
    raise Exception('You can only send JSON-serializable data')
  # send the length of the serialized data first
  socket.send('%d\n' % len(serialized))
  # send the serialized data
  socket.sendall(serialized)

def _recv(socket):
  # read the length of the data, letter by letter until we reach EOL
  length_str = ''
  char = socket.recv(1)
  while char != '\n':
    length_str += char
    char = socket.recv(1)
  total = int(length_str)
  # use a memoryview to receive the data chunk by chunk efficiently
  view = memoryview(bytearray(total))
  next_offset = 0
  while total - next_offset > 0:
    recv_size = socket.recv_into(view[next_offset:], total - next_offset)
    next_offset += recv_size
  try:
    deserialized = json.loads(view.tobytes())
  except (TypeError, ValueError), e:
    raise Exception('Data received was not in JSON format')
  return deserialized
