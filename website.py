from flask import Flask, render_template, request
#we are importing the function that makes predictions.
import os
from resume import resume_classification, similar_check
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["DEBUG"] = False

# Allowed files
ALLOWED_EXTENSIONS_VACANCY = {'pdf'}
ALLOWED_EXTENSIONS_RESUME = {'jpg','jpeg','png'}

UPLOAD_FOLDER = 'static/files/'

app.config['SECRET_KEY'] = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB upload limit

def allowed_file_vacancy(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_VACANCY

def allowed_file_resume(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_RESUME

@app.route("/", methods=['GET','POST'])
def upload_file():
    #initial webpage load
    if request.method == 'GET':
        return render_template('index.html')
    else: # if request method == 'POST'
        file_vacancy = request.files['vacancy']
        file_resume = request.files['resume']
        filename_resume = secure_filename(file_resume.filename)
        file_resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_resume))
        filename_vacancy = secure_filename(file_vacancy.filename)
        file_vacancy.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_vacancy))
        
        resume = (UPLOAD_FOLDER+filename_resume)
        vacancy = (UPLOAD_FOLDER+filename_vacancy)
        
        text_vacancy, result, score = resume_classification(resume)
        
        
        similar_score = similar_check(vacancy, text_vacancy)
        
        final_score = round(((score+similar_score) / 2),2)
        
        final_score = str(final_score)
        
        results = []
        answer = "<div class='col text-center'>your CV type is "+result+"</div>"
        results.append(answer)
        answer = "<div class='col text-center'>The match between your CV and the vacancy is : "+final_score+"%</div>"
        results.append(answer)
        
        return render_template('index.html', len=len(results), results=results)    

# Create a running list of result
results = []

# Launch Everyting
if __name__ == '__main__':
    app.run()
