import os,sys,getopt,logging
from flask import Flask,request,render_template,flash,send_file

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BERKAS = os.path.join(BASE_DIR, 'berkas')+os.path.sep
LOGS = os.path.join(BASE_DIR, 'logs')+os.path.sep
BERKAS_UNDUH = os.path.join(BERKAS, 'unduh')+os.path.sep
BERKAS_UNGGAH = os.path.join(BERKAS, 'unggah')+os.path.sep

if not os.path.exists(BERKAS_UNDUH):
    os.makedirs(BERKAS_UNDUH)
if not os.path.exists(BERKAS_UNGGAH):
    os.makedirs(BERKAS_UNGGAH)
if not os.path.exists(LOGS):
    os.makedirs(LOGS)

HELPER = '''python filetrans.py -p <port>'''

@app.route('/')
def filetrans():
    return render_template('filetrans.html')

@app.route('/unduh/',methods=['GET','POST'])
def download():
    if not os.path.exists(BERKAS_UNDUH):
        os.makedirs(BERKAS_UNDUH)
    FILES = [i for i in os.listdir(BERKAS_UNDUH) if os.path.isfile(BERKAS_UNDUH+i)]
    return render_template('download.html',daftar_berkas=FILES)

@app.route('/unduh/<nf>/',methods=['POST'])
def get_download(nf):
    if not os.path.exists(BERKAS_UNDUH):
        os.makedirs(BERKAS_UNDUH)
    if request.form['berkas']=='':
        flash('JANGAN DIKOSONGIN DONG!')
    elif request.form['berkas'] in [i for i in os.listdir(BERKAS_UNDUH) if os.path.isfile(BERKAS_UNDUH+i)]:
        logger.info('Client telah mengunduh berkas '+request.form['berkas'])
        return send_file(BERKAS_UNDUH+request.form['berkas'],attachment_filename=request.form['berkas'],as_attachment=True)
    else:
        flash('Berkasnya sudah tidak ada. Coba lagi!')
    return download()

@app.route('/unggah/',methods=['GET','POST'])
def upload():
    if not os.path.exists(BERKAS_UNDUH):
        os.makedirs(BERKAS_UNDUH)
    return render_template('upload.html')

@app.route('/unggah/<mk>/<kl>/<np>/<nf>/',methods=['POST'])
def get_upload(mk,kl,np,nf):
    if any([request.form[i]=='' for i in ['nama','npm','matkul','kelas']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return upload()
    elif 'file' not in request.files:
        flash('TIDAK ADA BAGIAN BERKAS')
        return upload()
    if not os.path.exists(BERKAS_UNGGAH+request.form['matkul']+os.path.sep):
        os.makedirs(BERKAS_UNGGAH+request.form['matkul']+os.path.sep)
    afile = request.files['file']
    if afile.filename == '':
        flash('BERKAS BELUM DIPILIH!')
        return upload()
    filename = os.path.basename(afile.filename)
    afile.save(os.path.join(BERKAS_UNGGAH+request.form['matkul']+os.path.sep+filename)
    logger.info(request.form['nama']+' ('+request.form['npm']+') dari '+request.form['matkul']+' kelas '+request.form['kelas']+' telah menggungah '+filename)
    return render_template('redirect_upload.html')
    
    

if __name__ == '__main__':
    try:
        opts,args = getopt.getopt(sys.argv[1:],'p:')
    except getopt.GetoptError:
        print(HELPER)
        sys.exit(2)

    opt = [i for i,j in opts]
    if any([i not in opt for i in ['-p']]) or opts == []:
        print(HELPER)
        sys.exit(2)

    for opt,arg in opts:
        if opt=='-p':
            try:
                p = int(arg)
            except:
                print(HELPER)
                sys.exit(2)
        else:
            print(HELPER)
            sys.exit(2)

    print()
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('{}filetrans.log'.format(LOGS))
        file_handler.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(logger_formatter)
        logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logger_formatter)
        logger.addHandler(console_handler)
        logger.info('==========START==========')
        logger.info('Letakkan berkas-berkas yang ingin dapat diunduh di folder unduh dalam folder berkas')
        logger.info('Berkas-berkas yang diunggah client ditaruh di folder unggah dalam folder berkas')
        app.secret_key = os.urandom(12)
        app.run(host='0.0.0.0',port=p)
    except:
        print(HELPER)
        sys.exit(2)
