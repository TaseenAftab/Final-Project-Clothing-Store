from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

import phonenumbers
from phonenumbers import NumberParseException
def login_required():
    if 'user_id' in session:
        return True
    else:
        return False
    



