name = "maya"
version = "2022"
description = "Maya 2022 package for Windows"
authors = ["placeholder"]
requires = []

def commands():
    env.MAYA_LOCATION = r"C:\Program Files\Autodesk\Maya2022"
    env.PATH.prepend(r"C:\Program Files\Autodesk\Maya2022\bin")
