# Tornado-Mail

A simple RESTful API based email client built using Tornado. It uses python's SMTP library to send email, IMAP library to receive emails. Tornado is used to serve the data to the reciever.

## Usage

First install Tornado by running `pip install tornado`, then change the configurations inside the `simple_mail.py`.

After that hit `python simple_mail.py`, and that should run the project.

To send email, make a post request with to `localhost:7777/sendmail` with perameters: 'to', 'body', 'message'.
To get emails, make a get request to `localhost:7777/getmail`.
