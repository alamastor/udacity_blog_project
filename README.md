# Bloggity: Udacity Blog Project
A multi-user blog - post articles, and view, like and comment on other users articles.
Deployed at <https://udacity-blog-project-144208.appspot.com>.

## Running in dev mode
1. Install the Google Cloud SDK <https://cloud.google.com/sdk/docs/>.
2. ``` bash
cd /path/to/project/dir
dev_appserver blog
```

## Running tests
``` bash
cd /path/to/project/dir
virtualenv venv
source venv/bin/activate
./generate_key.py
pip install -r requirements.txt
```
unit/integration/functional tests:
```./test_runner.py```
selenium functional tests:
```./test_runner.py --functional```

## Deploying
1. Install the Google Cloud SDK <https://cloud.google.com/sdk/docs/>.
2. Deploy the app:
``` bash
cd /path/to/project/dir
./generate_key.py
cd blog
gcloud app deploy app.yaml index.yaml
```
3. Wait 5 minutes for datastore indexes to be created.
