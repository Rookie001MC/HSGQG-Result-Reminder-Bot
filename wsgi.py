from facebook_messenger import app
from threading import Thread

def keep_alive() -> None:
    """ Wraps the web server run() method in a Thread object and starts the web server. """
    def run() -> None:
        app.run(host = '0.0.0.0', port = 1337)
    thread = Thread(target = run)
    thread.start()

if __name__ == "__main__":
    keep_alive()