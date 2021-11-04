import dash
import dash_auth

external_stylesheets = [
	{
		"href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
		"rel": "stylesheet",
	},
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Clover blockchain analytics"

CREDENTIALS = { 'user1': 'pass1', 'user2': 'pass2' }
auth = dash_auth.BasicAuth(app, CREDENTIALS)

server = app.server
app.config['suppress_callback_exceptions'] = True
