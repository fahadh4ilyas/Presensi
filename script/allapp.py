import os,json,sys,getopt,logging
from flask import Flask,request,abort,session,url_for,render_template,flash,jsonify,send_file

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE = os.path.join(BASE_DIR, 'database')+os.path.sep
BERKAS = os.path.join(BASE_DIR, 'berkas')+os.path.sep
LOGS = os.path.join(BASE_DIR, 'logs')+os.path.sep
BERKAS_UNDUH = os.path.join(BERKAS, 'unduh')+os.path.sep
BERKAS_UNGGAH = os.path.join(BERKAS, 'unggah')+os.path.sep

if not os.path.exists(DATABASE):
    os.makedirs(DATABASE)
if not os.path.exists(BERKAS_UNDUH):
    os.makedirs(BERKAS_UNDUH)
if not os.path.exists(BERKAS_UNGGAH):
    os.makedirs(BERKAS_UNGGAH)
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
KELAS_DICT = {}
for i in [j[0] for j in MATKUL_LIST]:
    if not os.path.exists(DATABASE+i+os.path.sep):
        os.makedirs(DATABASE+i+os.path.sep)
    KELAS_DICT[i] = []
    try:
        with open(DATABASE+i+os.path.sep+'kelas.txt','r') as afile:
            for k in afile.readlines():
                if k[-1]=='\n':
                    KELAS_DICT[i].append(k[:-1])
                elif k!='\n':
                    KELAS_DICT[i].append(k)
    except:
        with open(DATABASE+i+os.path.sep+'kelas.txt','w') as afile:
            afile.write('A\nB\nC\nD\nE')
        KELAS_DICT[i] = ['A','B','C','D','E']
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
KELAS = ''
PERTEMUAN = '1'
MEJA_LIST = []
MAX_MEJA = 0
PRESENSI_LIST = {}
HELPER = '''python allapp.py -p <port> -m <matkul> -k <kelas> -c <kapasitas_ruangan> -t <pertemuan ke> -w <password>
Daftar matkul:
'''+('\n'.join([i[0] for i in MATKUL_LIST]))+'''

Daftar kelas secara default:
'''+('\n'.join(KELAS_LIST))+'''

Untuk menambah matkul, tambahkan baris pada file matkul.txt di folder database dengan format: Singkatan Matkul,Nama Matkul
Unutk membuat kelas, tambahkan baris pada file kelas.txt di folder mata kuliah tersebut'''

@app.route('/')
def allapp():
    return render_template('allapp.html',aslab=False)

@app.route('/aslab/')
def allapp_aslab():
    return render_template('allapp.html',aslab=True)

@app.route('/login/',methods=['GET','POST'])
def login():
    return render_template('login.html',aslab=False,matkul=MATKUL,kelas=KELAS,meja=MEJA_LIST)

@app.route('/login/<mk>/<kl>/<np>/<mj>/',methods=['POST'])
def get_login(mk,kl,np,mj):
    global PRESENSI_LIST
    if any([request.form[i]=='' for i in ['nama','npm','meja']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return login()
    elif request.form['npm'] not in PRESENSI_LIST.keys():
        flash('KAMU BUKAN DARI KELAS '+KELAS+'! ISI PRESENSI KE ASLAB!')
        return login()
    else:
        PRESENSI_LIST[request.form['npm']]['Pertemuan'][PERTEMUAN] = request.form['meja']
        with open(DATABASE+MATKUL+os.path.sep+'kelas '+KELAS+'.json','w') as afile:
            json.dump(PRESENSI_LIST,afile)
        logger.info('[login] '+request.form['nama']+' ('+request.form['npm']+') telah login di meja '+request.form['meja'])
        return render_template('redirect_login.html',aslab=False)

@app.route('/aslab/login/',methods=['GET','POST'])
def login_aslab():
    return render_template('login.html',aslab=True,matkul=MATKUL,kelas=KELAS,meja=MEJA_LIST,daftar_kelas=KELAS_LIST)

@app.route('/aslab/login/<mk>/<kl>/<np>/<mj>/',methods=['POST'])
def get_login_aslab(mk,kl,np,mj):
    global PRESENSI_LIST
    if any([request.form[i]=='' for i in ['nama','npm','meja','kelas','hadir','password']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return login_aslab()
    elif request.form['password'] != PASSWORD:
        flash('PASSWORD SALAH!')
        return login_aslab()
    else:
        if request.form['kelas']==KELAS:
            TEMP_LIST = PRESENSI_LIST
        else:
            try:
                with open(DATABASE+MATKUL+os.path.sep+'kelas '+request.form['kelas']+'.json','r') as afile:
                    TEMP_LIST = json.load(afile)
            except:
                TEMP_LIST = {}
                try:
                    with open(DATABASE+MATKUL+os.path.sep+'kelas '+request.form['kelas']+'.txt','r') as afile:
                        for i in afile.readlines():
                            if i[-1] == '\n':
                                i = i[:-1]
                            elif i == '\n':
                                continue
                            temp = i.split(',')
                            TEMP_LIST[temp[0]] = {'Nama':temp[1],'Pertemuan':{PERTEMUAN:'0'}}
                    with open(DATABASE+MATKUL+os.path.sep+'kelas '+request.form['kelas']+'.json','w') as afile:
                        json.dump(TEMP_LIST,afile)
                except:
                    flash('Berkas "kelas '+request.form['kelas']+'.txt" belum ada. Buatlah dengan isi tiap baris dengan format: NPM,Nama\nAtau dengan program "regis.py"')
                    return login_aslab()
        if request.form['npm'] not in TEMP_LIST.keys():
            flash('KAMU BUKAN DARI KELAS '+request.form['kelas']+'! ISI PRESENSI DENGAN BENAR!')
            return login_aslab()
        if request.form['hadir'] == '1':
            TEMP_LIST[request.form['npm']]['Pertemuan'][PERTEMUAN] = request.form['meja']
            logger.info('[login] '+request.form['nama']+' ('+request.form['npm']+') kelas '+request.form['kelas']+' telah login di meja '+request.form['meja'])
        else:
            TEMP_LIST[request.form['npm']]['Pertemuan'][PERTEMUAN] = '0'
            logger.info('[login] '+request.form['nama']+' ('+request.form['npm']+') kelas '+request.form['kelas']+' telah ditandai tidak hadir')
        with open(DATABASE+MATKUL+os.path.sep+'kelas '+request.form['kelas']+'.json','w') as afile:
            json.dump(TEMP_LIST,afile)
        if request.form['kelas']==KELAS:
            PRESENSI_LIST = TEMP_LIST
        return render_template('redirect_login.html',aslab=True)

@app.route('/file/',methods=['GET','POST'])
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
        logger.info('[filetrans] Client telah mengunduh berkas '+request.form['berkas'])
        return send_file(BERKAS_UNDUH+request.form['berkas'],attachment_filename=request.form['berkas'],as_attachment=True)
    else:
        flash('Berkasnya sudah tidak ada. Coba lagi!')
    return download()

@app.route('/unggah/',methods=['GET','POST'])
def upload():
    if not os.path.exists(BERKAS_UNDUH):
        os.makedirs(BERKAS_UNDUH)
    return render_template('upload.html',matkul_list=[j[0] for j in MATKUL_LIST])

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
    afile.save(os.path.join(BERKAS_UNGGAH+request.form['matkul']+os.path.sep+filename))
    logger.info('[filetrans] '+request.form['nama']+' ('+request.form['npm']+') dari '+request.form['matkul']+' kelas '+request.form['kelas']+' telah menggungah '+filename)
    return render_template('redirect_upload.html')

@app.route('/check/',methods=['GET','POST'])
def check():
    return render_template('check.html',aslab=False)

@app.route('/check/<np>/',methods=['POST'])
def get_check(np):
    if any([request.form[i]=='' for i in ['nama','npm']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return check()
    else:
        max_pertemuan = 1
        alist = []
        for MATKUL in [i[0] for i in MATKUL_LIST]:
            adict = {}
            pertemuan = []
            for KELAS in KELAS_DICT[MATKUL]:
                try:
                    with open(DATABASE+MATKUL+os.path.sep+'kelas '+KELAS+'.json','r') as afile:
                        temp = json.load(afile)
                    if request.form['npm'] in temp.keys():
                        pertemuan = list(temp[request.form['npm']]['Pertemuan'].items())
                        pertemuan.sort(key=lambda x:int(x[0]))
                        pertemuan = [i[1] for i in pertemuan]
                        if len(pertemuan) > max_pertemuan:
                            max_pertemuan = len(pertemuan)
                        adict['kelas'] = KELAS
                        adict['Pertemuan'] = ['H' if i!='0' else 'TH' for i in pertemuan]
                        break
                except:
                    continue
            if pertemuan != []:
                adict['matkul'] = MATKUL
                alist.append(adict)
        for adict in alist:
            while len(adict['Pertemuan']) < max_pertemuan:
                adict['Pertemuan'].append('')
        logger.info('[check] '+request.form['nama']+' ('+request.form['npm']+') sedang memeriksa presensinya')
        return render_template('tabel_mahasiswa.html',
                               nama=request.form['nama'],
                               npm=request.form['npm'],
                               alist=alist,
                               max_pertemuan=max_pertemuan)

@app.route('/aslab/check/',methods=['GET','POST'])
def check_aslab():
    return render_template('check.html',aslab=True,matkul_list=[i[0] for i in MATKUL_LIST])

@app.route('/aslab/check/<mk>/<kl>/',methods=['POST'])
def get_check_aslab(mk,kl):
    if any([request.form[i]=='' for i in ['matkul','kelas','password']]):
        flash('JANGAN ADA YANG DIKOSONGIN DONG!')
        return check_aslab()
    elif request.form['password'] != PASSWORD:
        flash('PASSWORD SALAH!')
        return check_aslab()
    else:
        MATKUL = request.form['matkul']
        KELAS = request.form['kelas']
        nama_matkul = MATKUL_LIST[[i[0] for i in MATKUL_LIST].index(MATKUL)][1]
        banyak_pertemuan = 1
        try:
            with open(DATABASE+MATKUL+os.path.sep+'kelas '+KELAS+'.json','r') as afile:
                alist = list(json.load(afile).items())
                alist.sort(key=lambda x:int(x[0]))
        except:
            alist = []
        nomor = True
        if request.form["nomormeja"] != "true":
            nomor = False
        for i in range(len(alist)):
            temp = list(alist[i][1]['Pertemuan'].items())
            temp.sort(key=lambda x:int(x[0]))
            temp = [j[1] for j in temp]
            if len(temp) > banyak_pertemuan:
                banyak_pertemuan = len(temp)
            if request.form["nomormeja"] != "true":
                alist[i][1]['Pertemuan'] = ['H' if j!='0' else 'TH' for j in temp]
            else:
                alist[i][1]['Pertemuan'] = temp
        logger.info('[check] Presensi matkul '+request.form['matkul']+' kelas '+request.form['kelas']+' sedang diperiksa aslab')
        return render_template('tabel_aslab.html',
                               nama_matkul=nama_matkul,
                               kelas=KELAS,
                               banyak_pertemuan=banyak_pertemuan,
                               alist=alist,
                               nomor=nomor)

@app.route('/get_kelas/<matkul>')
def get_kelas(matkul):
    if matkul not in KELAS_DICT.keys():                                                                 
        return jsonify([])
    else:                                                                                    
        return jsonify(KELAS_DICT[matkul])

if __name__ == '__main__':
    try:
        opts,args = getopt.getopt(sys.argv[1:],'p:m:k:c:t:w:')
    except getopt.GetoptError:
        print(HELPER)
        sys.exit(2)

    opt = [i for i,j in opts]
    if any([i not in opt for i in ['-p','-m','-k','-c','-t','-w']]) or opts == []:
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

    KELAS_LIST = KELAS_DICT[MATKUL]

    HELPER = '''python allapp.py -p <port> -m <matkul> -k <kelas> -c <kapasitas_ruangan> -t <pertemuan ke> -w <password>
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
        elif opt in ['-m','-k']:
            continue
        elif opt=='-c':
            try:
                MAKS_MEJA = int(arg)
                assert MAKS_MEJA > 0
                MEJA_LIST = [str(i) for i in range(1,MAKS_MEJA+1)]
            except:
                print(HELPER)
                sys.exit(2)
        elif opt=='-t':
            try:
                PERTEMUAN = arg
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
    
    for opt,arg in opts:
        if opt=='-k':
            try:
                assert arg in KELAS_LIST
                KELAS = arg
            except:
                print(HELPER)
                sys.exit(2)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('{}allapp.log'.format(LOGS))
    file_handler.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter('%(levelname)s [%(asctime)s] [%(matkul)s-%(kelas)s-%(pertemuan)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(logger_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logger_formatter)
    logger.addHandler(console_handler)
    extra = {'matkul':MATKUL,'kelas':KELAS,'pertemuan':PERTEMUAN}
    logger = logging.LoggerAdapter(logger,extra)
    logger.info('==========START==========')

    try:
        logger.info('Akan mengambil daftar presensi dari berkas "kelas '+KELAS+'.json"')
        with open(DATABASE+MATKUL+os.path.sep+'kelas '+KELAS+'.json','r') as afile:
            PRESENSI_LIST = json.load(afile)
    except Exception as e:
        logger.info('Berkas "kelas '+KELAS+'.json" belum ada, akan mengambil daftar mahasiswa dari berkas "kelas '+KELAS+'.txt"')
        try:
            with open(DATABASE+MATKUL+os.path.sep+'kelas '+KELAS+'.txt','r') as afile:
                for i in afile.readlines():
                    if i[-1] == '\n':
                        i = i[:-1]
                    elif i == '\n':
                        continue
                    temp = i.split(',')
                    PRESENSI_LIST[temp[0]] = {'Nama':temp[1],'Pertemuan':{PERTEMUAN:'0'}}
            with open(DATABASE+MATKUL+os.path.sep+'kelas '+KELAS+'.json','w') as afile:
                json.dump(PRESENSI_LIST,afile)
        except:
            logger.warning('Berkas "kelas '+KELAS+'.txt" belum ada. Buatlah dengan isi tiap baris dengan format: NPM,Nama\nAtau dengan program "regis.py"')
            sys.exit(2)

    try:
        logger.info("Presensi akan disimpan di folder "+DATABASE+MATKUL)
        logger.info('Letakkan berkas-berkas yang ingin dapat diunduh di folder unduh dalam folder berkas')
        logger.info('Berkas-berkas yang diunggah client ditaruh di folder unggah dalam folder berkas')
        app.secret_key = os.urandom(12)
        app.run(host='0.0.0.0',port=p)
    except:
        print(HELPER)
        sys.exit(2)
