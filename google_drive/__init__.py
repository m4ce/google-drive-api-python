#
# __init__.py
#
# Author: Matteo Cerutti <matteo.cerutti@hotmail.co.uk>
#

import os

import httplib2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from apiclient.discovery import build

class DriveAPI:
  __acceptable_keys_list = ['oauth_client_id', 'oauth_client_secret', 'oauth_scope', 'oauth_token_file']

  def __init__(self, **kwargs):
    for k in kwargs.keys():
      if k in self.__acceptable_keys_list:
        setattr(self, k, kwargs[k])

    if 'oauth_scope' not in kwargs:
        self.oauth_scope = "https://www.googleapis.com/auth/drive.file"

    if 'oauth_token_file' not in kwargs:
      self.oauth_token_file = os.path.expanduser("~/.google-drive-oauth.json")

    self.service = None
    self.tree = {}

  def connect(self):
    http = self.authorize()
    self.service = build('drive', 'v2', http = http)
    self.tree = self.build_tree()

  def generate_token(self):
    flow = OAuth2WebServerFlow(self.oauth_client_id, self.oauth_client_secret, self.oauth_scope, redirect_uri = "urn:ietf:wg:oauth:2.0:oob")
    url = flow.step1_get_authorize_url()

    print("Go to the following link in your browser: %s" % url)
    code = raw_input("Enter verification code: ").strip()

    credentials = flow.step2_exchange(code)
    storage = Storage(self.oauth_token_file)
    storage.put(credentials)

    return storage 

  def read_token(self):
    return Storage(self.oauth_token_file)

  def authorize(self):
    try:
      with open(self.oauth_token_file) as f:
        storage = self.read_token()
    except IOError:
      storage = self.generate_token()

    credentials = storage.get()
    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)

    return http

  def list_dirs(self, **kwargs):
    q = ["mimeType = 'application/vnd.google-apps.folder'", "trashed = false"]
    if 'title' in kwargs and kwargs['title']:
      q.append("title = '%s'" % kwargs['title'])

    if 'parent_id' in kwargs and kwargs['parent_id']:
      q.append("'%s' in parents" % kwargs['parent_id'])

    return self.service.files().list(q = ' and '.join(q)).execute()

  def list_files(self, **kwargs):
    q = ["mimeType != 'application/vnd.google-apps.folder'", "trashed = false"]
    if 'title' in kwargs and kwargs['title']:
      q.append("title = '%s'" % kwargs['title'])

    if 'parent_id' in kwargs and kwargs['parent_id']:
      q.append("'%s' in parents" % kwargs['parent_id'])

    return self.service.files().list(q = ' and '.join(q)).execute()['items']

  def find_path(self, path, tree = None, parent_id = None):
    if tree is None:
      tree = self.tree

    folder_name = path.split('/')[0]

    if folder_name:
      if folder_name not in tree:
        return None
      else:
        return self.find_path('/'.join(path.split('/')[1:]), tree[folder_name]['children'], tree[folder_name]['id'])
    else:
      return parent_id

  def mkdir_p(self, path, tree = None, parent_id = None):
    if tree is None:
      tree = self.tree

    name = path.split('/')[0]

    if name != "":
      if name not in tree:
        folder_id = self.mkdir(name, parent_id = parent_id)
        tree[name] = {'id': folder_id, 'children': {}}
      else:
        folder_id = tree[name]['id']

      return self.mkdir_p('/'.join(path.split('/')[1:]), tree[name]['children'], folder_id)

    return parent_id

  def mkdir(self, name, **kwargs):
    body = {
      'title': name,
      'mimeType': "application/vnd.google-apps.folder"
    }

    if 'parent_id' in kwargs and kwargs['parent_id']:
      body['parents'] = [{'id': kwargs['parent_id']}]

    folder = self.service.files().insert(body = body).execute()

    return folder['id']

  def find_roots(self, dirs):
    roots = []

    for dir in dirs:
      parent = dir['parents'][0]
      if parent['isRoot']:
        if dir['id'] not in roots:
          roots.append(dir['id'])

    return roots

  def build_tree(self):
    dirs = self.list_dirs()
    roots = self.find_roots(dirs['items'])
    ids = self.map_ids(dirs['items'])

    tree = {}
    for root in roots:
      tree = self.build_root_tree(root, dirs['items'], ids)

    return tree

  def build_root_tree(self, parent_id, dirs, ids, ret = {}):
    ret[ids[parent_id]] = {'id': parent_id, 'children': {}}

    for dir in dirs:
      dir_parent = dir['parents'][0]
      if not dir_parent['isRoot']:
        if dir_parent['id'] == parent_id:
          self.build_root_tree(dir['id'], dirs, ids, ret[ids[parent_id]]['children'])

    return ret

  def map_ids(self, dirs):
    ids = {}

    for dir in dirs:
      ids[dir['id']] = dir['title']

    return ids

  def upload_file(self, local_file, **kwargs):
    title = os.path.basename(local_file)

    if 'mimetype' in kwargs:
      media_body = MediaFileUpload(local_file, mime_type = kwargs['mimetype'])
    else:
      media_body = MediaFileUpload(local_file)

    # check if file exists. If it does, update the existing file
    files = self.list_files(title = title, parent_id = parent_id)
    if len(files) > 0:
      return self.service.files().update(fileId = files[0]['id'], media_body = media_body).execute()
    else:
      body = {'title': title}
      if 'parent_id' in kwargs and kwargs['parent_id']:
        body.update({'parents': [{'id': kwargs['parent_id']}]})

      return self.service.files().insert(body = body, media_body = media_body).execute()
