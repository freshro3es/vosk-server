from app import create_app
import os

application = app = create_app()

if __name__ == '__main__':
    app.run(
        app,
        debug=True,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000))
    )
