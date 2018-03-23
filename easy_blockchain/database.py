import pickle
import json


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


def savetoJson(data, file_Name: str):
    with open(file_Name, 'w') as outfile:
        json.dump(data, outfile)


def loadfromJson(file_Name: str):
    with open(file_Name) as json_data:
        data = json.load(json_data)
    return data
