import os,json,sys,getopt
from flask import Flask,request,abort,session,url_for,render_template,flash,jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE = os.path.join(BASE_DIR, 'database')+os.path.sep

if not os.path.exists(DATABASE):
    os.makedirs(DATABASE)

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
PASSWORD = '1234'
HELPER = '''python check.py -p <port> -w <password>'''

@app.route('/')
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
        return render_template('tabel_mahasiswa.html',
                               nama=request.form['nama'],
                               npm=request.form['npm'],
                               alist=alist,
                               max_pertemuan=max_pertemuan)

@app.route('/aslab/')
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
        opts,args = getopt.getopt(sys.argv[1:],'p:w:')
    except getopt.GetoptError:
        print(HELPER)
        sys.exit(2)

    opt = [i for i,j in opts]
    if any([i not in opt for i in ['-p','-w']]) or opts == []:
        print(HELPER)
        sys.exit(2)

    for opt,arg in opts:
        if opt=='-p':
            try:
                p = int(arg)
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

    try:
        app.secret_key = os.urandom(12)
        app.run(host='0.0.0.0',port=p)
    except:
        print(HELPER)
        sys.exit(2)