import os,json,sys,getopt,logging
from flask import Flask,request,abort,session,url_for,render_template,flash

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE = os.path.join(BASE_DIR, 'database')+os.path.sep
LOGS = os.path.join(BASE_DIR, 'logs')+os.path.sep

if not os.path.exists(DATABASE):
    os.makedirs(DATABASE)
if not os.path.exists(LOGS):
    os.makedirs(LOGS)

try:
    MATKUL_LIST = []
    with open(DATABASE+'matkul.txt','r') as afile:
        for i in afile.readlines():
            if i[-1]=='\n':
                MATKUL_LIST.append(i[:-1].split(','))
            elif i!='\n':
                MATKUL_LIST.append(i.split(','))
except:
    with open(DATABASE+'matkul.txt','w') as afile:
        afile.write('MD1,Matematika Dasar 1\nMD2,Matematika Dasar 2\nALPROG,Algoritma dan Pemrograman\nMETNUM,Metode Numerik')
    MATKUL_LIST = [['MD1','Matematika Dasar 1'],
                   ['MD2','Matematika Dasar 2'],
                   ['ALPROG','Algoritma dan Pemrograman'],
                   ['METNUM','Metode Numerik']]
try:
    KELAS_LIST = []
    with open(DATABASE+'kelas_default.txt','r') as afile:
        for i in afile.readlines():
            if i[-1]=='\n':
                KELAS_LIST.append(i[:-1])
            elif i!='\n':
                KELAS_LIST.append(i)
except:
    with open(DATABASE+'kelas_default.txt','w') as afile:
        afile.write('A\nB\nC\nD\nE')
    KELAS_LIST = ['A','B','C','D','E']
PASSWORD = '1234'
MATKUL = ''
DAFTAR_MAHASISWA = {}
MAKS_MEJA = 0
HELPER = '''python regis.py -p <port> -m <matkul> -c <kapasitas_ruangan> -w <password>
Daftar matkul:
'''+('\n'.join([i[0] for i in MATKUL_LIST]))+'''

Daftar kelas secara default:
'''+('\n'.join(KELAS_LIST))+'''

Untuk menambah matkul, tambahkan baris pada file matkul.txt di folder database dengan format: Singkatan Matkul,Nama Matkul
Unutk membuat kelas, tambahkan baris pada file kelas.txt di folder mata kuliah tersebut'''

@app.route('/')
def regis():
    return render_template('regis.html',aslab=False,matkul=MATKUL,daftar_kelas=KELAS_LIST)

@app.route('/<mk>/<kl>/<np>/',methods=['POST'])
def get_regis(mk,kl,np):
    global DAFTAR_MAHASISWA
    temp = []
    for i in DAFTAR_MAHASISWA.values():
        temp += i
    if any([request.form[i]=='' for i in ['nama','npm','kelas']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return regis()
    elif len(DAFTAR_MAHASISWA[request.form['kelas']]) >= MAKS_MEJA:
        flash('KELAS '+request.form['kelas']+' SUDAH PENUH! PILIH KELAS LAIN!')
        return regis()
    elif request.form['npm'] in [i[0] for i in temp]:
        for i in KELAS_LIST:
            if request.form['npm'] in [j[0] for j in DAFTAR_MAHASISWA[i]]:
                flash(request.form['npm']+' SUDAH TERDAFTAR DI KELAS '+i+'!')
                return regis()
    else:
        DAFTAR_MAHASISWA[request.form['kelas']].append([request.form['npm'],request.form['nama']])
        logger.info(request.form['nama']+' ('+request.form['npm']+') telah regis di kelas '+request.form['kelas'])
        with open(DATABASE+MATKUL+os.path.sep+'kelas '+request.form['kelas']+'.txt','w') as afile:
            afile.write('\n'.join([','.join(i) for i in DAFTAR_MAHASISWA[request.form['kelas']]]))
        return render_template('redirect_regis.html',aslab=False)

@app.route('/aslab/')
def remove_aslab():
    return render_template('regis.html',aslab=True,matkul=MATKUL,daftar_kelas=KELAS_LIST)

@app.route('/aslab/<mk>/<kl>/<np>/',methods=['POST'])
def get_remove_aslab(mk,kl,np):
    global DAFTAR_MAHASISWA
    if any([request.form[i]=='' for i in ['nama','npm','kelas','password']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return remove_aslab()
    elif request.form['password'] != PASSWORD:
        flash('PASSWORD SALAH!')
        return remove_aslab()
    elif request.form['npm'] not in [i[0] for i in DAFTAR_MAHASISWA[request.form['kelas']]]:
        flash(request.form['npm']+' TIDAK TERDAFTAR DI KELAS '+request.form['kelas'])
        return remove_aslab()
    else:
        temp = [i[0] for i in DAFTAR_MAHASISWA[request.form['kelas']]].index(request.form['npm'])
        DAFTAR_MAHASISWA[request.form['kelas']].remove(DAFTAR_MAHASISWA[request.form['kelas']][temp])
        logger.info(request.form['nama']+' ('+request.form['npm']+') telah dihapus dari kelas '+request.form['kelas'])
        with open(DATABASE+MATKUL+os.path.sep+'kelas '+request.form['kelas']+'.txt','w') as afile:
            afile.write('\n'.join([','.join(i) for i in DAFTAR_MAHASISWA[request.form['kelas']]]))
        return render_template('redirect_regis.html',aslab=True)

if __name__ == '__main__':
    try:
        opts,args = getopt.getopt(sys.argv[1:],'p:m:c:w:')
    except getopt.GetoptError:
        print(HELPER)
        sys.exit(2)

    opt = [i for i,j in opts]
    if any([i not in opt for i in ['-p','-m','-c','-w']]) or opts == []:
        print(HELPER)
        sys.exit(2)

    for opt,arg in opts:
        if opt=='-m':
            try:
                assert arg in [i[0] for i in MATKUL_LIST]
                MATKUL = arg
            except:
                print(HELPER)
                sys.exit(2)

    if not os.path.exists(DATABASE+MATKUL):
        os.makedirs(DATABASE+MATKUL)
        with open(DATABASE+MATKUL+os.path.sep+'kelas.txt','w') as afile:
            afile.write('\n'.join(KELAS_LIST))
    else:
        try:
            KELAS_LIST = []
            with open(DATABASE+MATKUL+os.path.sep+'kelas.txt','r') as afile:
                for i in afile.readlines():
                    if i[-1]=='\n':
                        KELAS_LIST.append(i[:-1])
                    elif i!='\n':
                        KELAS_LIST.append(i)
        except:
            with open(DATABASE+MATKUL+os.path.sep+'kelas.txt','w') as afile:
                afile.write('A\nB\nC\nD\nE')
            KELAS_LIST = ['A','B','C','D','E']

    for i in KELAS_LIST:
        DAFTAR_MAHASISWA[i] = []

    HELPER = '''python regis.py -p <port> -m <matkul> -c <kapasitas_ruangan> -w <password>
Matkul yang dipilih: '''+MATKUL+'''

Daftar kelas:
'''+('\n'.join(KELAS_LIST))+'''

Untuk menambah matkul, tambahkan baris pada file matkul.txt di folder database dengan format: Singkatan Matkul,Nama Matkul
Unutk membuat kelas, tambahkan baris pada file kelas.txt di folder mata kuliah tersebut'''

    for opt,arg in opts:
        if opt=='-p':
            try:
                p = int(arg)
            except:
                print(HELPER)
                sys.exit(2)
        elif opt=='-m':
            continue
        elif opt=='-c':
            try:
                MAKS_MEJA = int(arg)
                assert MAKS_MEJA > 0
            except:
                print(HELPER)
                sys.exit(2)
        elif opt=='-w':
            try:
                PASSWORD = arg
            except:
                print(HELPER)
                sys.exit(2)
        else:
            print(HELPER)
            sys.exit(2)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('{}regis.log'.format(LOGS))
    file_handler.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter('%(levelname)s [%(asctime)s] [%(matkul)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(logger_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logger_formatter)
    logger.addHandler(console_handler)
    extra = {'matkul':MATKUL}
    logger = logging.LoggerAdapter(logger,extra)
    logger.info('==========START==========')
    logger.info('Akan Mengambil daftar mahasiswa jika ada')
    for i in KELAS_LIST:
        try:
            logger.info('Mengambil daftar mahasiwa kelas '+i)
            with open(DATABASE+MATKUL+os.path.sep+'kelas '+i+'.txt','r') as afile:
                for j in afile.readlines():
                    if j[-1] == '\n':
                        j = j[:-1]
                    elif j == '\n':
                        continue
                    DAFTAR_MAHASISWA[i].append(j.split(','))
        except:
            logger.info('Tidak ada daftar mahasiswa kelas '+i)
            with open(DATABASE+MATKUL+os.path.sep+'kelas '+i+'.txt','w') as afile:
                afile.write('\n'.join([','.join(j) for j in DAFTAR_MAHASISWA[i]]))

    try:
        logger.info("Daftar Mahasiswa akan disimpan di folder "+DATABASE+MATKUL)
        app.secret_key = os.urandom(12)
        app.run(host='0.0.0.0',port=p)
    except:
        print(HELPER)
        sys.exit(2)
