import uuid
from datetime import datetime, timedelta
from pathlib import Path
import json

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
        self.path = Path(__file__).parent / 'relatorio.json'
        self.base_data = self.init_data()
        pass
    
    def init_data(self):
        with open(self.path, 'r') as file:
            return json.load(file)
    
    def add(self, project: Project) -> str:
        uuid_str = str(uuid.uuid4())
        self.base_data[uuid_str] = json.loads(project.to_string())
        
        with open(self.path, 'w') as file:
            json.dump(
                self.base_data,
                file,
                ensure_ascii=False,
                indent=2
            )
        return f'{uuid_str} -> \n{'\n'.join(project.to_string().split(','))}'

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
                    ...
                elif answer == 3:
                    ...
                elif answer == 5:
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
        
if __name__ == '__main__':
    Main()