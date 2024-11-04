from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Video  # Import db and Video from models.py
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'  # Path to the database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your_secret_key'

# Initialize db with app
db.init_app(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

# Helper function for file type check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    videos = Video.query.all()  # Retrieve all videos from the database
    return render_template('home.html', videos=videos)

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash("No file part")
#             return redirect(request.url)
        
#         file = request.files['file']

#         if file.filename == '':
#             flash("No selected file")
#             return redirect(request.url)

#         if file and allowed_file(file.filename):
#             filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             # Create and save new video entry
#             new_video = Video(filename=filename)
#             db.session.add(new_video)
#             db.session.commit()

#             return render_template('upload_success.html', video_filename=filename)
#         else:
#             flash("File type not allowed")
#             return redirect(request.url)

#     return render_template('upload.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("Received a POST request for file upload.")
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files['file']
        print(f"Filename received: {file.filename}")

        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Create and save new video entry
            new_video = Video(filename=filename)
            db.session.add(new_video)
            db.session.commit()  # Commit the changes to the database
            print(f"Saved video entry: {new_video.filename}")

            return render_template('upload_success.html', video_filename=filename)
        else:
            flash("File type not allowed")
            return redirect(request.url)

    return render_template('upload.html')


@app.route('/delete/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if video:
        # Delete the video file from the filesystem
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], video.filename))
        db.session.delete(video)
        db.session.commit()
        flash("Video deleted successfully.")
    else:
        flash("Video not found.")
    
    return redirect(url_for('home'))

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
