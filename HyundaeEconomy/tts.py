from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import tkinter.messagebox
from gtts import gTTS
from tkinter.scrolledtext import ScrolledText
import random
from datetime import date
import os
#import subprocess, sys, os

class Window(Frame):

    def __init__(self, master):

        global st,status_label

        self.master = master
        self.master.title("낭독기")
        self.master.geometry("400x450+200+200")

        #상단기본메뉴
        menu = Menu(self.master)
        self.master.configure(menu=menu)
        #file
        file=Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="New file", command=mOpen)
        file.add_command(label="Clear", command=deleteText)
        file.add_command(label="Quit", command=quit)
        #Edit
        edit=Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit)
        edit.add_command(label="언어선택", command=doNothing)
        edit.add_command(label="기타", command=doNothing)
        #help
        help=Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help)
        help.add_command(label="Update", command=doNothing)
        help.add_command(label="About", command=doNothing)

        #로고및 제목
        title = Frame(master, width=400, height=200, bg = "bisque4")
        title.pack(fill=X)

        m_image = Image.open("microphone-1172260_1280.jpg")
        m_image = m_image.resize((500,300), Image.ANTIALIAS)
        #m_image = ImageTk.PhotoImage(m_image)
        #title_label = Label(title, image=m_image, bg = "bisque4", fg="azure2")
        #title_label.image = m_image
        #title_label.place(relx=0.5, rely=0.5, anchor=CENTER)

        t_title = Label(title, text="낭독기", bg="black", fg="white")
        labelfont = ('굴림체', 20, 'bold')
        t_title.config(font=labelfont)
        t_title.place(x=10, y=10, relx=0.2)

        c_title = Label(title, text="제작자 : sss", bg="black", fg="gray67")
        c_title.place(relx=0.65, rely=0.85)


        #text content
        text_frame = Frame(master, width=400, height=170, padx=5, pady=5, bg="gray84")
        text_frame.pack(fill=X)
        st = ScrolledText(text_frame, padx=5, pady=5, height=10, bg="white", fg="black")
        st.insert(INSERT, "글을 입력하면 컴퓨터가 읽어 줍니다.")
        st.insert(END, " 저장된 txt파일을 불러 올 수 있습니다.")
        st.pack(fill=BOTH, expand=True)

        #버튼들
        bttnMainFrame = Frame(master, width=400, height=70,bg="gray84")
        bttnMainFrame.pack(fill=BOTH, expand=True)
        button_frame = Frame(bttnMainFrame, width=400, height=70, pady=10, bg="gray84")
        button_frame.pack()

        my_bttn1 = Button(button_frame, text="듣기및저장", padx=5, command=playText).grid(row=0, column=0)
        my_bttn2 = Button(button_frame, text="새로작성",padx=5, command=deleteText).grid(row=0, column=1)
        #my_bttn3 = Button(button_frame, text="저장하기", padx=5, command=doNothing).grid(row=0, column=2)
        my_bttn4 = Button(button_frame, text="문서불러오기", padx=5, command=mOpen).grid(row=0, column=3)


        #status
        status_frame = Frame(master, width=400, height=70, bg="gray84")
        status_frame.pack(side=BOTTOM, fill=X)
        status_label = tkinter.Label(status_frame, text= "V1.0", bg="gray84").pack()



#***DEF

def doNothing():
    print("Do nothing...!")

#단순 경고창
def messagebox(message):
    tkinter.messagebox.showinfo("알림", message)
    return

#종료
def quit():
    exit()

#상태바 메세지
def statusChange(txt):
    #status_label.configure(text=txt)
    pass

#함수 - 텍스트창에 내용 변경하기
def changeText(my_text):
    st.delete("0.0", END)
    st.insert("1.0", my_text) #첫줄부터 삽입됨
    #st.insert(INSERT, my_text)
    st.insert(END, " ")
    #내용 가져오기 print(st.get("1.0", END))

def deleteText():
    st.delete("0.0", END)
    print("deleted ALL")

#듣기 실행
def playText():
    my_text= st.get("1.0", END)
    #입력창에 텍스트가 없을 때 경고문 출력
    print(len(my_text))
    if my_text and len(my_text) < 5:
        messagebox("텍스트가 없거나 너무 짧습니다.")
        return

    #파일로 mp3파일 저장
    tts= gTTS(text=my_text, lang="ko")
    m_ram = random.randint(1,100)
    t = date.today()
    m_mpfile = ("tts-%s-%d.mp3" % (t, m_ram))
    tts.save(m_mpfile)
    #return_code = subprocess.call(["afplay", m_mpfile])
    os.system("start %s" % m_mpfile)
    #파일 저장 실패시 경고문 출력

    print("save and play Ok!")

    #다시 불러와서 들려줌 그런데 MP3를 실행하는 모듈이 파이썬3에 맞는게 없다???
    #준비중


def mOpen():

    #statusChange("파일열기중")

    # define options for opening or saving a file
    file_opt = options = {}
    options['defaultextension'] = '.txt'
    options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
    options['initialdir'] = 'C:\\'
    #options['initialfile'] = '.txt'
    options['parent'] = root
    options['title'] = 'Open my txt files'

    mFile = filedialog.askopenfile(mode="r", **file_opt)

    if mFile == None:
        print("파일열기 취소함")
    else:
        my_text = mFile.read()
        #파일을 열고서 읽어서 입력창에 넣어 주기 함수 실행
        changeText(my_text)


root = Tk()

app = Window(root)

root.mainloop()