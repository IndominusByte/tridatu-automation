import requests, json, sys
from time import sleep
from rich.console import Console

console = Console()

class Automation:
    def __init__(self,base_address: str):
        self.session = requests.Session()
        self.base_address = base_address
        self.csrf_access_token = None
        self.time_sleep = 0.5

    def login(self,email: str = 'user@example.com', password: str = 'string') -> None:
        url = self.base_address + '/users/login'
        res = self.session.post(url,json={'email': email, 'password': password})
        self.csrf_access_token = self.session.cookies['csrf_access_token']
        console.log('[green]login complete[/green], message: {}'.format(res.json()['detail']))
        sleep(self.time_sleep)

    def create_address(self,data_address: dict = json.loads(open('address.json','rb').read())) -> None:
        url = self.base_address + '/address/create'
        res = self.session.post(url,json=data_address,headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log('[green]add address complete[/green], message: {}'.format(res.json()['detail']))
        sleep(self.time_sleep)

    def create_brands(self,name: str, file: str) -> None:
        url = self.base_address + '/brands/create'
        res = self.session.post(url,
            files={'file': open(f'images/brand/{file}','rb')},
            data={'name': name},
            headers={'X-CSRF-TOKEN': self.csrf_access_token}
        )
        console.log('[green]brand [blue]{}[/blue] complete[/green], message: {}'.format(name,res.json()['detail']))
        sleep(self.time_sleep)

    def create_categories(self,name: str) -> int:
        # create categories
        url = self.base_address + '/categories/create'
        res = self.session.post(url,json={'name': name},headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log('[green]categories [blue]{}[/blue] complete[/green], message: {}'.format(name,res.json()['detail']))
        sleep(self.time_sleep)
        url = self.base_address + '/categories/all-categories'
        res = self.session.get(url + '?with_sub=false')
        return [x for x in res.json() if x['categories_name'] == name][0]['categories_id']

    def create_sub_categories(self,id_cat: int, name: str) -> int:
        # create sub categories
        url = self.base_address + '/sub-categories/create'
        res = self.session.post(url,json={'name': name, 'category_id': id_cat},headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log('[green]sub-categories [blue]{}[/blue] complete[/green], message: {}'.format(name,res.json()['detail']))
        sleep(self.time_sleep)
        # get sub categories id
        url = self.base_address + '/categories/all-categories?with_sub=true'
        res = self.session.get(url)
        return [x for x in res.json() if x['sub_categories_name'] == name and x['categories_id'] == id_cat][0]['sub_categories_id']

    def create_item_sub_categories(self,id_sub_cat: int, name: str) -> None:
        # create item sub
        url = self.base_address + '/item-sub-categories/create'
        res = self.session.post(url,json={'name': name, 'sub_category_id': id_sub_cat},headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log('[green]item-sub-categories [blue]{}[/blue] complete[/green], message: {}'.format(name,res.json()['detail']))
        sleep(self.time_sleep)

    def create_variants(self,variant_data: dict, name_product: str) -> str:
        url = self.base_address + '/variants/create-ticket'
        res = self.session.post(url,json=variant_data,headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log(
            '[green]variants [blue]{}[/blue] complete[/green], message: {}'.format(
                name_product,res.json().get('detail') or res.json().get('ticket')
            )
        )
        sleep(self.time_sleep)
        return res.json().get('ticket')

    def create_wholesale(self,items: list, variant: str, name_product: str) -> str:
        url = self.base_address + '/wholesale/create-ticket'
        res = self.session.post(url,json={'variant': variant,'items': items},headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log(
            '[green]wholesale [blue]{}[/blue] complete[/green], message: {}'.format(
                name_product,res.json().get('detail') or res.json().get('ticket')
            )
        )
        sleep(self.time_sleep)
        return res.json().get('ticket')

    def create_products(self,**kwargs) -> None:
        data = {key:value for key,value in kwargs['product_data'].items() if key not in ['image_product','image_variant','image_size_guide']}

        files = list()
        [
            files.append(("image_product", (f"{x}", open(f"images/products/{x}",'rb'),"image/jpeg")))
            for x in kwargs['product_data']['image_product']
        ]
        [
            files.append(("image_variant", (f"{x}", open(f"images/products/{x}",'rb'),"image/jpeg")))
            for x in kwargs['product_data']['image_variant']
        ]
        if image_size_guide := kwargs['product_data']['image_size_guide']:
            files.append(("image_size_guide", (f"{image_size_guide}", open(f"images/{image_size_guide}",'rb'),"image/jpeg")))

        data.update({'ticket_variant': self.create_variants(kwargs['variant'],data['name'])})
        data.update({
            'ticket_wholesale': self.create_wholesale(kwargs['wholesale']['items'],data['ticket_variant'],data['name'])
            if len(kwargs['wholesale']['items']) > 0 else None
        })

        url = self.base_address + '/products/create'
        res = self.session.post(url,data=data,files=files,headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log('[green]products [blue]{}[/blue] complete[/green], message: {}'.format(data['name'],res.json()['detail']))
        sleep(self.time_sleep)

    def get_products_id(self) -> list:
        url = self.base_address + '/products/all-products'
        res = self.session.get(url + '?page=1&per_page=100')
        return [(x['products_id'],x['products_name']) for x in res.json()['data']]

    def set_alive_products(self,id_: int, name: str) -> None:
        url = self.base_address + '/products/alive-archive/'
        res = self.session.put(url + str(id_),headers={'X-CSRF-TOKEN': self.csrf_access_token})
        console.log('[green]products-alive [blue]{}[/blue] complete[/green], message: {}'.format(name,res.json()['detail']))
        sleep(self.time_sleep)


if __name__ == '__main__':
    environtment = sys.argv[1]
    if environtment.lower() == 'local':
        base_address = "http://{}:8000".format(input("Input your ip address: "))
    elif environtment.lower() == 'prod':
        base_address = "https://backend.mentimun-mentah.tech"
    else:
        exit(1)

    with console.status("[bold green]Working on tasks...") as status:
        automate = Automation(base_address=base_address)
        automate.login()

        [automate.create_address() for x in range(20)]

        [automate.create_brands(brand['name'],brand['file']) for brand in json.loads(open('brand.json','rb').read())]

        for category in json.loads(open('category.json','rb').read()):
            id_cat = automate.create_categories(category['name_category'])
            for sub_category in category['sub_categories']:
                id_sub_cat = automate.create_sub_categories(id_cat,sub_category['name_sub_category'])
                for item_sub_category in sub_category['item_sub_categories']:
                    automate.create_item_sub_categories(id_sub_cat,item_sub_category['name_item_sub_category'])

        [automate.create_products(**product) for product in json.loads(open('product.json','rb').read())]

        [automate.set_alive_products(id_,name) for id_,name in automate.get_products_id()]
