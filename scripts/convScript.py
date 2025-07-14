import html
import os

for filename in os.listdir('csv'):   
    path='csv/'+filename
    path_out='csv_out/'+filename
    with open(path, 'r', encoding='utf-8') as f_in:
        content = f_in.read()

    decoded_content = html.unescape(content)

    with open(path_out, 'w', encoding='utf-8') as f_out:
        f_out.write(decoded_content)