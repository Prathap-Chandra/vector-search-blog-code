from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)  # Change 8000 to your desired port

