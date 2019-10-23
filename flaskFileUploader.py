from flask import Flask,abort,render_template,request,redirect,url_for, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug import secure_filename
import os


app = Flask(__name__, static_folder='build/static', template_folder="build")


# Need cors to resolve cors conflict
cors = CORS(app)

# Create upload directory to save files to
uploads_dir = os.path.join(app.instance_path, 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

# Restrict file types saved to dircd 
ALLOWED_EXTENSIONS = set(['mp3', 'mp4', 'json'])

# Checks filename extension type
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#serve react app
@app.route('/')
def serve():
        return send_from_directory('build/', 'index.html')


# Handles POST of file
@app.route('/uploadfile', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            #No file part
            return redirect(request.url)
            
        #Gets file from form data
        file = request.files['file']

        if file.filename == '':
            #No file selected for uploading
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            #Generate secure file name
            filename = secure_filename(file.filename)
            #Save file to dir
            file.save(os.path.join(uploads_dir, filename))
            #File successfully uploaded
            return redirect('/uploadfile')
        else:
            #File type not allowed - accepted types are mp3, mp4, JSON
            return redirect(request.url)


# Handles POST of colour value
@app.route('/uploadcol', methods=['POST'])
def upload_col():
    if request.method == 'POST':
        #Get col value from form data
        colour = request.form.get('colour')
        name_of_file = "col_values"
        #Gen .json type file in uploads dir
        completeName = os.path.join(uploads_dir, name_of_file+".json")   
        #Write to file JSON col
        file1 = open(completeName, "w")
        jsonstring = '{"colour" : ' + colour + '}'
        file1.write(jsonstring)
        file1.close()

    return
    

if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0')
