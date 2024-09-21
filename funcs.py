from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

def login_required():
    if 'user_id' in session:
        return True
    else:
        return False
    



