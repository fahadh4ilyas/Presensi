import os,sys,getopt
from flask import Flask,request,render_template,flash,send_file

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BERKAS = os.path.join(BASE_DIR, 'berkas')+os.path.sep

if not os.path.exists(BERKAS):
    os.makedirs(BERKAS)

HELPER = '''python download.py -p <port>'''

@app.route('/')
def download():
    if not os.path.exists(BERKAS):
        os.makedirs(BERKAS)
    FILES = [i for i in os.listdir(BERKAS) if os.path.isfile(BERKAS+i)]
    return render_template('download.html',daftar_berkas=FILES)

@app.route('/unduh/<nf>/',methods=['POST'])
def get_download(nf):
    if not os.path.exists(BERKAS):
        os.makedirs(BERKAS)
    if request.form['berkas']=='':
        flash('JANGAN DIKOSONGIN DONG!')
    elif request.form['berkas'] in [i for i in os.listdir(BERKAS) if os.path.isfile(BERKAS+i)]:
        return send_file(BERKAS+request.form['berkas'],attachment_filename=request.form['berkas'],as_attachment=True)
    else:
        flash('Berkasnya sudah tidak ada. Coba lagi!')
    return download()

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

    print('Letakkan berkas-berkas yang ingin dapat diunduh di folder berkas')
    try:
        app.secret_key = os.urandom(12)
        app.run(host='0.0.0.0',port=p)
    except:
        print(HELPER)
        sys.exit(2)