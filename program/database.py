import os
from shutil import copyfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = DATABASE = os.path.join(BASE_DIR, 'database')+os.path.sep

print('''Ini adalah program untuk membuat database untuk presensi praktikum.
Pastikan program ini berada di folder program!
''')

input('Tekan ENTER untuk melanjutkan ')

print('Memeriksa apakah folder "database" ada')
if not os.path.exists(DATABASE):
    print('Membuat folder "database"')
    os.makedirs(DATABASE)
    print('Folder "database" berhasil dibuat\n')

input('Tekan ENTER untuk melanjutkan ')

print('Memeriksa apakah berkas "matkul.txt" ada')
print('''Berkas "matkul.txt" berisi daftar nama mata kuliah yang dipraktikumkan.
Format penulisannya adalah: Singkatan mata kuliah,Nama mata kuliah
Contoh isi matkul.txt:
MD1,Matematika Dasar 1
MD2,Matematika Dasar 2
ALPROG,Algoritma dan Pemrograman
METNUM,Metode Numerik''')
if not os.path.isfile(DATABASE+'matkul.txt'):
    print('Berkas "matkul.txt" tidak ada!\nProses membuat berkas "matkul.txt"')
    print('Jika ingin mengikuti contoh, ketik y. Jika tidak, ketik lainnya.')
    if input('pilih?(y/n) ') == 'y':
        with open(DATABASE+'matkul.txt','w') as afile:
            afile.write('''MD1,Matematika Dasar 1
MD2,Matematika Dasar 2
ALPROG,Algoritma dan Pemrograman
METNUM,Metode Numerik''')
    else:
        matkul = ''
        temp = 'a'
        print('''Masukkan mata kuliah dengan format: Singkatan mata kuliah,Nama mata kuliah
Tekan ENTER tanpa mengisi mata kuliah jika sudah selesai''')
        while temp != '':
            temp = input('Masukkan mata kuliah: ')
            if len(temp.split(','))!=2:
                print('Mohon masukkan dengan format: Singkatan mata kuliah,Nama mata kuliah')
            else:
                matkul += (temp+'\n')
        while matkul[-1] == '\n':
            matkul = matkul[:-1]
        with open(DATABASE+'matkul.txt','w') as afile:
            afile.write(matkul)
    print('''Berkas "matkul.txt" berhasil dibuat di folder database.
Anda dapat mengubah isi berkas secara manual jika ingin mengubah mata kuliah praktikum.\n''')

input('Tekan ENTER untuk melanjutkan ')

print('Memeriksa apakah berkas "kelas_default.txt" ada')
print('''Berkas "kelas_default.txt" berisi daftar nama kelas yang dipraktikumkan secara default.
Jadi, setiap mata kuliah secara default akan mengandung kelas di dalam berkas "kelas_default.txt".
Untuk mengubah kelas di sebuah mata kuliah, ubah berkas "kelas.txt" di folder mata kuliah tersebut.
Contoh isi kelas_default.txt:
A
B
C
D
E''')
if not os.path.isfile(DATABASE+'kelas_default.txt'):
    print('Berkas "kelas_default.txt" tidak ada!\nProses membuat berkas "kelas_default.txt"')
    print('Jika ingin mengikuti contoh, ketik y. Jika tidak, ketik lainnya.')
    if input('pilih?(y/n) ') == 'y':
        with open(DATABASE+'kelas_default.txt','w') as afile:
            afile.write('A\nB\nC\nD\nE')
    else:
        kelas = ''
        temp = 'a'
        print('''Masukkan kelas yang diinginkan
Tekan ENTER tanpa mengisi kelas jika sudah selesai''')
        while temp != '':
            temp = input('Masukkan mata kuliah: ')
            kelas += (temp+'\n')
        while kelas[-1] == '\n':
            kelas = kelas[:-1]
        with open(DATABASE+'kelas_default.txt','w') as afile:
            afile.write(kelas)
    print('''Berkas "kelas_default.txt" berhasil dibuat di folder database.
Anda dapat mengubah isi berkas secara manual jika ingin mengubah kelas secara default.\n''')

input('Tekan ENTER untuk melanjutkan ')

print('Membuat folder mata kuliah dan berkas "kelas.txt"')
with open(DATABASE+'matkul.txt','r') as afile:
    matkul_list = []
    for i in afile.readlines():
        if i[-1] == '\n':
            matkul_list.append(i[:-1].split(','))
        elif i != '\n':
            matkul_list.append(i.split(','))
for i in [j[0] for j in matkul_list]:
    if not os.path.exists(DATABASE+i+os.path.sep):
        print('Membuat folder mata kuliah '+i)
        os.makedirs(DATABASE+i+os.path.sep)
    print('Folder mata kuliah '+i+' telah dibuat.')
    if not os.path.isfile(DATABASE+i+os.path.sep+'kelas.txt'):
        print('Membuat berkas "kelas.txt" di folder mata kuliah '+i)
        copyfile(DATABASE+'kelas_default.txt',DATABASE+i+os.path.sep+'kelas.txt')
    print('Berkas "kelas.txt" telah dibuat')

input('\nProses membuat folder database telah selesai. Tekan ENTER untuk keluar ')
