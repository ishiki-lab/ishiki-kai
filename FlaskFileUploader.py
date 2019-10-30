from flask import Flask,abort,render_template,request,redirect,url_for, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug import secure_filename
import os
import sys
import logging
from colorsys import rgb_to_hsv


app = Flask(__name__, static_folder='build/static', template_folder="build")
logging.basicConfig(level=logging.DEBUG)

# Need cors to resolve cors conflict
cors = CORS(app)

# Restrict file types saved to dircd 
ALLOWED_EXTENSIONS = set(['mp3', 'mp4', 'json'])

# Create upload directory to save files to
uploads_dir = os.path.join('/media/usb/', 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

def logger(message):
    app.logger.info("INFO: " + message)
    sys.stdout.flush()

# Checks filename extension type
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Serve React app @ https://github.com/LUSHDigital/lrpi_scentroom_ui
@app.route('/')
def serve():
    return send_from_directory('build/', 'index.html')


# Handles POST request of file
@app.route('/uploadfile', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            #No file part
            return jsonify({'response': 404, 'audio_saved': False, 'description': 'No file found', 'path': request.url})

        #Gets file from form data
        file = request.files['file']

        if file.filename == '':
            #No file selected for uploading
            return jsonify({'response': 500, 'audio_saved': False, 'description': 'No file selected', 'path': request.url})
        
        if file and allowed_file(file.filename):
            #Generate secure file name
            filename = secure_filename(file.filename)
            #Save file to dir
            file.save(os.path.join(uploads_dir, filename))
            #File successfully uploaded
            return jsonify({'response': 200, 'audio_saved': True, 'description': 'Audio Saved', 'path': request.url})
        else:
            return jsonify({'response': 500, 'audio_saved': False, 'description': 'File type not allowed - accepted types are mp3, mp4, JSON', 'path': request.url})
    
    return jsonify({'response': 500, 'audio_saved': False, 'description': 'Could not save audio file', 'path': request.url})



# Handles POST request of colour value
@app.route('/uploadcol', methods=['POST'])
def upload_col():
    if request.method == 'POST': 
         
        #Get col value from form data
        colour = request.form.get('colour')

        if colour is not None:
            if lightingEvent(colour):
                return jsonify({'response' : 200, 'col_saved': True, 'description': 'Colour saved', 'path': request.url})
        else:   
            return jsonify({'response': 500, 'col_saved': False, 'description': 'Colour value non type', 'path': request.url})

    return jsonify({'response': 500, 'col_saved': False, 'description': 'Colour upload failed', 'path': request.url})


#Function appends col hex values to .srt file type
def lightingEvent(col_hex_val):
    scentroom_event = LightingEvent(col_hex_val)
    return scentroom_event.to_srt(str(uploads_dir))


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'response':404, 'description': 'Page Not Found' + str(e)})


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'response':500, 'description': 'Internal Server Error' + str(e)})


#Lighting event class
class LightingEvent: 

    #set colour value on init
    def __init__(self, col_val): 
        if col_val is not None:
            #convert hex value to rgb
            col_val = col_val.lstrip('#')
            rgb = tuple(int(col_val[i:i+2], 16) for i in (0, 2, 4))
            r = float(rgb[0])
            g = float(rgb[1])
            b = float(rgb[2])
            #convert rgb value to hsv
            h,s,v = rgb_to_hsv(r,g,b)
            self.hsv_col_val = str(h) + ',' + str(s) + ',' + str(v)
            self.rgbw_col_val = self.rgb_to_rgbw(r,g,b)


    #creates srt file with col val at path
    def to_srt(self, path):

        if self.hsv_col_val is not None: 
            file_name = "col_lighting_event"
            completeName = os.path.join(path, file_name + ".srt")
            #srt file for write operation
            srt_file = open(completeName, "w")
            #srt seq num
            srt_file.write("1\n")
            #srt marker
            srt_file.write("00:00:00,000 --> 00:02:00,000\n")
            #srt HUE col val
            srt_file.write("HUE1(" + self.hsv_col_val + ");\n")
            #srt DMX col val
            srt_file.write("RGBW(" + self.rgbw_col_val + ");\n")
            srt_file.close()
            return True
        
        return False
        

    #converts rgb values to rgbw
    def rgb_to_rgbw(self, Ri, Gi, Bi):
        Wo = min(Ri,Gi,Bi)
        Ro = Ri - Wo
        Go = Gi - Wo
        Bo = Bi - Wo
        return(str(int(Ro)) + ', ' + str(int(Go)) + ', ' + str(int(Bo)) + ', ' + str(int(Wo)))
        
        

if __name__ == '__main__':
    logger("Hi!")
    logger("Uploads directory is: " + uploads_dir)
    app.run(port=os.environ['PORT'], host='0.0.0.0')






