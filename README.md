# Python library for Google Drive API
This is a simple Python library that allows to interact with the Google Drive REST API.

Pull requests to add additional API features are very welcome. I only implemented what I needed.

## Install
To install it simply issue the following command:

```
pip install google-drive-api
```

## Usage
```
from google_drive import DriveAPI
drive = DriveAPI(oauth_client_id = "CLIENT_ID", oauth_client_secret = "SECRET", oauth_scope = "SCOPE")
drive.connect()
```

Create a path recursively. It will return the ID of the last folder created.
```
folder_id = drive.mkdir_p("folder1/folder2/folder3")
```

Upload a file into the root directory
```
drive.upload_file("file.txt")
```

Upload a file and set the mime type
```
drive.upload_file("file.png", mime_type = "image/png")
```

Upload a file into a specific directory
```
folder_id = drive.find_path("folder1/folder2")
drive.upload_file("file.pdf", parent_id = folder_id)
```

## Contact
Matteo Cerutti - matteo.cerutti@hotmail.co.uk
