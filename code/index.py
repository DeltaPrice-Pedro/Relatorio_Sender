import uuid
from datetime import datetime, timedelta
from pathlib import Path
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from os import getenv
from re import sub
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

class Email:
    PATH_MESSAGE = Path(__file__).parent / 'src' / 'doc' / 'base_message.html'

    def __init__(self) -> None:
        self.smtp_server = getenv("SMTP_SERVER","")
        self.smtp_port = getenv("SMTP_PORT", 0)

        self.smtp_username = getenv("EMAIL_SENDER","")
        self.smtp_password = getenv("PASSWRD_SENDER","")

        self.sign_up = '▲'
        self.sign_down = '▼'

        self.ref_cor = {
            'IPCA': 'lightyellow',
            'RENDA': 'lightblue',
            'EDUCA': 'lightpink',
            'PREFIXADO': 'lightcyan',
            'SELIC': 'lightcoral'
        }
        pass

    def create_message(self, move: list[tuple]) -> str:
        format_data = []
        for item in move:
            item = self.update_values(item)

            item_str = ''.join(
                [f'<td> {data} </td>' for data in item[1:]]
            )

            color = self.get_color(item[1])
            format_data.append(
                 f'<tr style="background-color: {color};"> {item_str} </tr>'
            )

        with open (self.PATH_MESSAGE, 'r', encoding='utf-8') as file:
            text_message = file.read()
            return Template(text_message)\
                .substitute(infos =  ''.join(x for x in format_data))

    def update_values(self, item):
        y = list(item)

        color_font = 'green' if float(y[4].replace('.','').replace(',','.')) > 0 else 'red'
        signal = f'% {self.sign_up if float(y[4]) > 0 else self.sign_down}'

        y[4] = f'<span style="color:{color_font}";> {y[4].replace('.',',')} {signal} </span>'
        
        y[1] = sub(r"\d", "", item[1])
        return tuple(y)
        
    def get_color(self, name_row):
        for key, color in self.ref_cor.items():
            if key in name_row:
                return color
        return 'white'

    def send(self, texto_email: str, to: str) -> None:
        mime_multipart = MIMEMultipart()
        mime_multipart['From'] = self.smtp_username
        mime_multipart['To'] = to
        mime_multipart['Subject'] = f'Atualização Tesouro Direto {datetime.strftime(datetime.now(), '%d/%m - %H:%M')}'

        mime_multipart.attach(MIMEText(texto_email, 'html', 'utf-8'))

        self._open_server(mime_multipart)

    def _open_server(self, mime_multipart: MIMEMultipart) -> None:
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(mime_multipart)

class Project:
    def __init__(self, nome: str, finish: int, thinker: str):
        today = datetime.now()
        self.data = {
            "name": nome,
            "start": today.strftime('%d/%m/%Y'),
            "finish": (today + timedelta(days=finish)).strftime('%d/%m/%Y'),
            "thinker": thinker,
            "state": 'Inativo',
            "grip": 'Inutilizado'
        }
        pass
    
    def to_string(self):
        return json.dumps(self.data)
    
class Resume:
    def __init__(self):
        self.path = Path(__file__).parent / 'src' / 'relatorio.json'
        self.base_data = self._init_data()
        pass
    
    def _init_data(self) -> dict:
        with open(self.path, 'r') as file:
            return json.load(file)
        
    def names(self) -> dict:
        names = {}
        for key, value in self.base_data.items():
            names[key] = value['name']
        return names
    
    def specs(self, uuid: str):
        return json.dumps(self.base_data[uuid])
    
    def add(self, project: Project) -> str:
        uuid_str = str(uuid.uuid4())
        self.base_data[uuid_str] = json.loads(project.to_string())
        self.update_file()
        return f'{uuid_str} -> \n{'\n'.join(project.to_string().split(','))}'
    
    def remove(self, uuid: str):
        removed_name = self.base_data[uuid]['name']
        del self.base_data[uuid]
        self.update_file()
        return removed_name
    
    def update(self, uuid: str, spec: str, new_value: str):
        old_value = self.base_data[uuid][spec]
        self.base_data[uuid][spec] = new_value
        self.update_file()
        return old_value, new_value
    
    def test_spec(self, uuid: str, spec: str,):
        self.updater[uuid][spec]

    def update_file(self):
        with open(self.path, 'w') as file:
            json.dump(
                self.base_data,
                file,
                ensure_ascii=False,
                indent=2
            )

    def to_string(self):
        return json.dumps(self.base_data, indent=2)

class Main:
    def __init__(self):
        self.resume = Resume()
        self.end = False
        self.menu()
        pass
    
    def error(self, message: str, method):
        print(f'{"!"*3}{message}{"!"*3}')
        print('(Pressione qualquer tecla para continuar)')
        input()
        return method()
    
    def options(self) -> int:
        try:
            print(f'{"#"*40}\n{"#"*7} Gerenciador de Relatório {"#"*7}\n{"#"*40}')
            print('>> Projeto\n1) Criar\n2) Atualizar\n3) Apagar\n\n>> Relatório\n4) Visualizar\n5) Enviar\n\n6) Sair')
            return int(input('RESPOSTA: '))
        except TypeError:
            return self.error('Tipo errado', self.options)
            
    def menu(self):
        try:
            while(self.end == False):
                answer = self.options()
                print('\n')
                if answer == 1:
                    proj_add = self.resume.add(self.create_project())
                    print('\n--Projeto Adcionado--')
                    print(proj_add)
                    input()
                elif answer == 2:
                    old_value, new_value = self.resume.update(self.update_project())
                    print('\n--Projeto Atualizado--')
                    print(f'{old_value} -> {new_value}')
                    input()
                elif answer == 3:
                    proj_remove = self.resume.remove(self.remove_project())
                    print('\n--Projeto Removido--')
                    print(proj_remove)
                    input()
                elif answer == 4:
                    print(self.resume.to_string())
                    input()
                elif answer == 5:
                    self.end = True
                elif answer == 6:
                    self.end = True
                else:
                    raise Exception('Fora das opções disponíveis')
        except Exception as e:
            self.error(e.__str__(), self.menu)
            
    def create_project(self):
        try:
            name = input('Nome: ')
            thinker = input('Idealizador: ')
            finish = int(input('Previsão de término: '))
            return Project(name, finish, thinker)
        except TypeError:
            return self.error('Tipo errado', self.create_project)
        except Exception as e:
            return self.error(e.__str__(), self.create_project)
        
    def remove_project(self) -> str:
        try:
            print('Qual dos projetos deseja remover?')
            keys = self.show_names()
            return keys[int(input('\nRESPOSTA: ')) - 1]
        except TypeError:
            return self.error('Tipo errado', self.remove_project)
        except Exception as e:
            return self.error(e.__str__(), self.remove_project)
        
    def update_project(self):
        try:
            print('Qual dos projetos deseja atualizar?')
            keys = self.show_names()
            uuid = keys[int(input('\nRESPOSTA: ')) - 1]
            return uuid, self.input_spec(uuid)
        except TypeError:
            return self.error('Tipo errado', self.remove_project)
        except Exception as e:
            return self.error(e.__str__(), self.remove_project)

    def input_spec(self, uuid):
        try:
            print('\n' + self.resume.specs(uuid))
            spec = input('Propriedade desejada: ')
            self.resume.test_spec(spec)
            new_value = input('Novo valor: ')
            return spec, new_value
        except TypeError:
                return self.error('Tipo errado', self.remove_project)
        except Exception as e:
            return self.error(e.__str__(), self.remove_project)

    def show_names(self):
        count = 1
        keys = []
        for key, name in self.resume.names().items():
            print(f'{count}) {name}')
            keys.append(key)
            count = count + 1
        return keys
    
    
        
if __name__ == '__main__':
    Main()