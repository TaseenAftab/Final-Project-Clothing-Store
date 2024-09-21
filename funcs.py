from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

def login_required():
    if 'user_id' in session:
        return True
    else:
        return False
    

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


