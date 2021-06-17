
def createIndex(read_file):
    index = list(range(2, len(read_file)+2))
    read_file['Row'] = index
    return read_file
