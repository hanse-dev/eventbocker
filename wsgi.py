from app.app import app, init_app

if __name__ == "__main__":
    # Initialize the app before running
    init_app()
    app.run()
