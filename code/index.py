import uuid
from datetime import datetime, timedelta
from pathlib import Path
import json

class Project:
    def __init__(self, nome: str,inicio: datetime, termino: datetime, idealizador: str, aderencia: bool):
        self.data = {
            "name": nome,
            "termino": termino.strftime('%d/%m/%Y'),
            "termino": termino.strftime('%d/%m/%Y'),
            "idealizador": idealizador,
            "aderencia": 'Utilizado' if aderencia else 'Inutilizado'
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
        uuid = str(uuid.uuid4())
        with open(self.path, 'w') as file:
            json.dump(
                project.to_string(),
                file,
                ensure_ascii=False,
                indent=2
            )
        return f'{uuid} -> {project.to_string()}'

class Main:
    def __init__(self):
        self.resume = Resume()
        self.menu()
        self.end = False
        pass
    
    def error(self, message: str, method):
        print(f'{"!"*3}{message}{"!"*3}')
        print('(Pressione qualquer tecla para continuar)')
        input()
        return method()
    
    def options(self) -> int:
        try:
            print(f'{"#"*10}\n{"#"*10}Gerenciador de Relatório{"#"*10}\n{"#"*10}')
            print('>> Projeto\n1) Criar\n2) Atualizar\n3) Apagar\n\n>> Enviar <<\n4) [Sair]')
            return int(input())
        except TypeError:
            return self.error('Tipo errado', self.options)
            
    def menu(self):
        try:
            while(self.end == False):
                answer = self.options()
                if answer == 1:
                    today = datetime.now()
                    name, thinker, finish  = self.create_project()
                    proj_add = self.resume.add(Project(
                        name,
                        today,
                        today + timedelta(days=finish),
                        thinker, 
                        False
                    ))
                    print(proj_add)
                    input()
                elif answer == 2:
                    ...
                elif answer == 3:
                    ...
                elif answer == 4:
                    end = True
                else:
                    raise Exception('Fora das opções disponíveis')
        except Exception as e:
            self.error(e.__str__, self.menu)
            
    def create_project(self):
        try:
            print('Nome: ')
            name = input()
            print('Idalizador: ')
            thinker = input()
            print('Previsão de término: ')
            finish = int(input())
            return name, thinker, finish
        except TypeError:
            return self.error('Tipo errado', self.create_project)
        
        
        
            
        

if __name__ == '__main__':
    Main()