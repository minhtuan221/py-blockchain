import pickle


def savetoFile(data, file_Name: str):
    # open the file for writing
    fileObject = open(file_Name, 'wb')

    # this writes the object a to the
    # file named 'testfile'
    pickle.dump(data, fileObject)

    # here we close the fileObject
    fileObject.close()


def loadfromFile(file_Name: str):
    # we open the file for reading
    fileObject = open(file_Name, 'rb')
    # load the object from the file into var b
    data = pickle.load(fileObject)
    # print(data)
    return data
