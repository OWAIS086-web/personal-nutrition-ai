from nutrition import create_app, db  # make sure db is imported from your package

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ✅ fix indentation

    app.run(debug=True, host='0.0.0.0', port=5000)
