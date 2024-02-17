from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from tkinter import messagebox
from docx import Document
from langchain import hub
import tkinter as tk
import ctypes
import glob
import bs4
import os





os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = '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'
os.environ['OPENAI_API_KEY'] = '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'

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def parse_folder(folder_path):
    texts = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".docx"):
            file_path = os.path.join(folder_path, file_name)
            text = extract_text_from_docx(file_path)
            texts.append(text)
    return texts

folder_path = "Датасет/"
docs = parse_folder(folder_path)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.create_documents(docs)

vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def delete_word(event):
    text = prompt_entry.get("1.0", tk.END)
    words = text.split()
    if len(words) > 0:
        new_text = ' '.join(words[:-1])
        prompt_entry.delete("1.0", tk.END)
        prompt_entry.insert(tk.END, new_text)

def generate_answer():
    answer_entry.configure(state = 'normal')
    question = prompt_entry.get()
    answer = rag_chain.invoke(question)
    answer_entry.delete('1.0', tk.END) 
    answer_entry.insert(tk.END, answer)
    answer_entry.configure(state = 'disabled')

root = tk.Tk()
root.title("AI помощник ИТМО")
root.geometry('%sx%s' % (screensize[0], screensize[1]))

prompt_label = tk.Label(root, text="Введите промпт:")
prompt_label.pack()

prompt_entry = tk.Text(root, wrap='word', width=60, height=5)
prompt_entry.pack()

generate_button = tk.Button(root, text="Сгенерировать ответ", command=generate_answer)
generate_button.pack()

answer_label = tk.Label(root, text="Ответ:")
answer_label.pack()
answer_entry = tk.Text(root, wrap='word', width=60, height=5)
answer_entry.pack()

prompt_entry.configure(font=("Courier", 18))
answer_entry.configure(font=("Courier", 18))
answer_entry.configure(state = 'disabled')

prompt_entry.bind("<Control-BackSpace>", delete_word)

root.mainloop()