How to use this app

initiate docker swarm service locally by running:
`sub-xnat2bids.sh <project ID>`

You will be promted to enter your xnat login credentials if no token is found in your project directory.

# TODO: package username and password into same encrypted token (auth.py)

sub-xnat2bids.sh will mount your auth token to the created service. If you are having authentication issues, it could have something to do with access permissions to this file.

The service will then automatically download all nifti and json files from any exams found in your working.lst file as a zip, unzip, then move those files from .../derivatives/bidsonly/<exam_no_dir> to .../rawdata in bids structure. It will place any files uncaught by bids conditions in a folder called '/sort' adjacent to the session's '/anat', '/fmap', '/func' etc folders.
