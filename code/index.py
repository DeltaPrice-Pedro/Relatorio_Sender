import uuid
from datetime import datetime, timedelta
from pathlib import Path
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from os import getenv, environ
from traceback import print_exc
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

class Email:
    PATH_MESSAGE = Path(__file__).parent / 'src' / 'doc' / 'base_message.html'

    def __init__(self) -> None:
        self.smtp_server = getenv("SMTP_SERVER","")
        self.smtp_port = getenv("SMTP_PORT", 0)

        self.smtp_addresse = json.loads(environ["ADDRESSE"])
        self.smtp_username = getenv("EMAIL_SENDER","")
        self.smtp_password = getenv("PASSWRD_SENDER","")

        pass

    def create_message(self, projects: list[tuple]) -> str:
        back_color = False
        format_data = []
        for item in projects:
            item_str = ''.join(
                [f'<td style="text-align: center;"> {data} </td>' for data in item]
            )

            color = 'lightgray' if back_color else 'gainsboro'
            back_color = not back_color
            format_data.append(
                 f'<tr style="background-color: {color};"> {item_str} </tr>'
            )

        with open (self.PATH_MESSAGE, 'r', encoding='utf-8') as file:
            text_message = file.read()
            return Template(text_message)\
                .substitute(infos =  ''.join(x for x in format_data))

    def send(self, text_email: str,) -> None:
        for to in self.smtp_addresse:
            mime_multipart = MIMEMultipart()
            mime_multipart['From'] = self.smtp_username
            mime_multipart['Subject'] = f'Relatório Pedro {datetime.strftime(datetime.now(), '%d/%m/%Y')}'
            mime_multipart.attach(MIMEText(text_email, 'html', 'utf-8'))
            mime_multipart['To'] = to
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
        return json.dumps(self.data, indent= 2)
    
class Resume:
    def __init__(self):
        self.path = Path(__file__).parent / 'src' / 'doc' / 'relatorio.json'
        self.base_data = self._init_data()
        pass
    
    def _init_data(self) -> dict:
        with open(self.path, 'r') as file:
            return json.load(file)
        
    def send_email(self):
        email = Email()
        text_message = email.create_message(self._structured_projects())
        email.send(text_message)

    def _structured_projects(self) -> list[tuple]:
        projects = []
        for i in self.base_data.values():
            project = ()
            for j in i.values():
                project = project + (j,)
            projects.append(project)
        return projects

        
    def names(self) -> dict:
        names = {}
        for key, value in self.base_data.items():
            names[key] = value['name']
        return names
    
    def specs(self, uuid: str):
        return json.dumps(self.base_data[uuid], indent=2)
    
    def add(self, project: Project) -> str:
        uuid_str = str(uuid.uuid4())
        self.base_data[uuid_str] = json.loads(project.to_string())
        self.update_file()
        return f'{uuid_str} -> \n{project.to_string()}'
    
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
        self.base_data[uuid][spec]

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
                    uuid, spec, new_value = self.update_project()
                    old_value, new_value = self.resume.update(uuid, spec, new_value)
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
                    self.resume.to_string()
                    resp = input('Confirma o envio? ')
                    if resp == 'n':
                        continue
                    self.resume.send_email()
                    print('\n!!Projetos Enviados!!')
                    input()
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
            spec, new_value = self.input_spec(uuid)
            return uuid, spec, new_value
        except TypeError:
            return self.error('Tipo errado', self.update_project)
        except Exception as e:
            return self.error(e.__str__(), self.update_project)

    def input_spec(self, uuid):
        try:
            print('\nPropriedade desejada: ')
            print(self.resume.specs(uuid) + '\n')
            spec = input('RESPOSTA: ')
            self.resume.test_spec(uuid, spec)
            new_value = input('\nNovo valor: ')
            return spec, new_value
        except TypeError:
                return self.error('Tipo errado', self.input_spec)
        except Exception as e:
            print_exc()
            return self.error(e.__str__(), self.input_spec)

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