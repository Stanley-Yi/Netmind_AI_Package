# generate multiple pdfs
import json
from agents.pdf_from_html import Gen_pdf
gen_pdf_tool = Gen_pdf()

bank_info = {}
htmls = ['html/statement-template-0.html','html/statement-template-1.html','html/statement-template-2.html']
history = ''
for idx in range(98,100):
    pdf_path = f'pdf/bs{idx}.pdf'
    img_path=f'img/bk{idx}.png'
    html_path = htmls[idx%3]
    data = gen_pdf_tool(history=history, pdf_path=pdf_path, img_path=img_path, html_path=html_path)
    bank_info[img_path] = data

    history = history + str(data) + '\n' 
    print(idx)

with open('bank_info.json', 'w') as f:
    json.dump(bank_info, f)