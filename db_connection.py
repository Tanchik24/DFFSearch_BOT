import os
from dff.context_storages import context_storage_factory

db_uri = "mysql+asyncmy://{}:{}@localhost:3307/{}".format(
    os.environ["MYSQL_USERNAME"],
    os.environ["MYSQL_PASSWORD"],
    os.environ["MYSQL_DATABASE"],
)
db = context_storage_factory(db_uri)