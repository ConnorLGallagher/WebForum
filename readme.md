# Requirments: 
    import os
    from flask import Flask, render_template, session, redirect, url_for, request, make_response
    from flask_sqlalchemy import SQLAlchemy
    from datetime import datetime

    Python 3.9.7, as the default anaconda base

    Anaconda Envoirment also included in files just in case only use if needed

    -Connor- I did have to download a sqlite3.dll and extract it into the module directory of sqlite, specifics are in the stack overflow linked. I do not know if it is necessay for this project as I did this for one of the previous labs.

# references

    Documentation that was broadly referenced used but not precisely copied
    https://getbootstrap.com/docs/5.2/getting-started/introduction/
    https://flask-sqlalchemy.palletsprojects.com/en/2.x/
    https://www.sqlalchemy.org/
    https://www.sqlite.org/docs.html
    
    if sqlite3.dll import error is present
    https://www.sqlite.org/download.html
    https://stackoverflow.com/questions/54876404/unable-to-import-sqlite3-using-anaconda-python
# github link
    this will look pretty stupid once I push it to github, but I do want to include it in the zip submission
    https://github.com/trevrodd/WebApp_forum
