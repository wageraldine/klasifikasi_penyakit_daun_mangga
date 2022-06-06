from flask import render_template
from flask import Flask, flash, request, redirect
from werkzeug.utils import secure_filename
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from tensorflow.compat.v1.keras.backend import set_session
import tensorflow as tf
import numpy as np
import os


app = Flask(__name__)
app.config["DEBUG"] = False

# Allowed files
ALLOWED_EXTENSIONS = {'jpg','jpeg','png'}

# Make sure nothing malicious is uploaded
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'static/files/'

app.config['SECRET_KEY'] = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB upload limit

@app.route("/", methods=['GET','POST'])
def upload_file():
    #initial webpage load
    if request.method == 'GET':
        return render_template('index.html')
    else: # if request method == 'POST'
        if 'file' not in request.files:
            flash('No File part')
            return redirect(request.url)
        file = request.files['file']
        # if user dosen't select file, browser may also
        # submit an empty part without filename
        if file.filename == '':
            flash('Tidak ada foto yang dipilih !')
            return redirect(request.url)
        # if dosen't look like an image file
        if not allowed_file(file.filename):
            flash('Masukan file gambar dengan tipe exetensi '+str(ALLOWED_EXTENSIONS))
            return redirect(request.url)
        # When the user upload a file with good parameter
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            test_image = image.load_img(UPLOAD_FOLDER+'/'+filename, target_size=(150, 150))
            test_image = image.img_to_array(test_image)
            test_image = np.expand_dims(test_image, axis=0)
            
            myModel = load_model('model_penyakit_daun_mangga_adam.h5')
            result = myModel.predict(test_image)
            image_src = '/'+UPLOAD_FOLDER+'/'+filename
            results = []
            if result[0][0] == 1 :
                answer = "<div class='col text-center'><img width=150 height=150 src='"+image_src+"' class=img-'thumbnail'/><h5>Daun terdeteksi penyakit Antrachnose "+str(result[0][0])+"</h5></div>"
            elif result[0][1] == 1 :
                answer = "<div class='col text-center'><img width=150 height=150 src='"+image_src+"' class=img-'thumbnail'/><h5>Daun terdeteksi penyakit Black Shooty "+str(result[0][1])+"</h5></div>"
            elif result[0][2] == 1 :
                answer = "<div class='col text-center'><img width=150 height=150 src='"+image_src+"' class=img-'thumbnail'/><h5>Daun mangga sehat "+str(result[0][2])+"</h5></div>"
            results.append(answer)
            return render_template('index.html', len=len(results), results=results)            

# Create a running list of result
results = []

# Launch Everyting
if __name__ == '__main__':
    app.run()
