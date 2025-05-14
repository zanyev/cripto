import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import pandas as pd
import datetime as dt

orders = pd.read_csv('./assets/order_status.csv',index_col=0).T
# Obtendo credenciais do Gmail a partir das variáveis de ambiente
gmail_user = os.environ.get('Email')
gmail_password = os.environ.get('EmailPass')

def send_email(subject, body, to_email, body_type='plain'):
    # Verificando se as credenciais estão presentes
    if not gmail_user or not gmail_password:
        print('Por favor, configure as variáveis de ambiente "Email" e "EmailPass".')
        return

    # Criando os cabeçalhos do e-mail
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # Anexando o corpo do e-mail ao MIME message
    msg.attach(MIMEText(body, body_type))

    # Conectando ao servidor SMTP do Gmail e enviando o e-mail
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        print('E-mail enviado com sucesso!')
    except Exception as e:
        print(f'Falha ao enviar o e-mail: {e}')

# Exemplo de uso para enviar um e-mail com corpo HTML
html_body = f"""
<html>
  <body>
    <h1>Basket Order</h1>
    <p>Ordens Diárias</b>.</p>
    {orders.to_html()}
  </body>
</html>
"""

send_email(f'Long-Short - {dt.date.today().strftime('%Y-%m-%d')}', html_body, 'relima223@gmail.com', 'html')
