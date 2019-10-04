import gzip
import pickle
import json


def save_gzip_pickle(object, path_file, protocol=-1):
    """Saves a compressed object to disk
    """
    in_file = gzip.GzipFile(path_file, 'wb')
    in_file.write(pickle.dumps(object, protocol))
    in_file.close()


def load_gzip_pickle(filename):
    """Loads a compressed object from disk
    """
    in_file = gzip.GzipFile(filename, 'rb')
    buffer = ""
    while True:
        data = in_file.read()
        if data == "":
            break
        buffer += data
    object = pickle.loads(buffer)
    in_file.close()
    return object


def save_pickle(object, path_file, protocol=-1):
    """Saves an object to disk
    """
    with open(path_file, 'wb') as handle:
        pickle.dump(object, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(filename):
    """Loads a compressed object from disk
    """
    with open(filename, 'rb') as handle:
        object = pickle.load(handle)

    return object


def save_json(object, path_file):
    with open(path_file, 'w') as fp:
        json.dump(object, fp)


def load_json(path_file):
    with open(path_file, 'r') as fp:
        data = json.load(fp)
    return data
