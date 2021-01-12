import requests, json
from time import sleep
from rich.console import Console

console = Console()

base_address = "http://{}:{}".format(input("Input your ip address: "),input("Input your port: "))
session = requests.Session()
csrf_access_token = None

def login(email: str = 'user@example.com', password: str = 'string'):
    global csrf_access_token
    url = base_address + '/users/login'
    res = session.post(url, json={'email': email, 'password': password})
    csrf_access_token = session.cookies['csrf_access_token']
    console.log('[green]login complete[/green], message: {}'.format(res.json()['detail']))
    sleep(1)

def create_brands(name_brand: str = 'nike'):
    url = base_address + '/brands/create'
    res = session.post(url,
        files={'file': open('images/1.jpeg','rb')},
        data={'name': name_brand},
        headers={'X-CSRF-TOKEN': csrf_access_token}
    )
    console.log('[green]brand complete[/green], message: {}'.format(res.json()['detail']))
    sleep(1)

def create_categories(name_cat: str) -> int:
    # create categories
    url = base_address + '/categories/create'
    res = session.post(url, json={'name': name_cat},headers={'X-CSRF-TOKEN': csrf_access_token})
    console.log('[green]categories [blue]{}[/blue] complete[/green], message: {}'.format(name_cat,res.json()['detail']))
    sleep(1)
    # get categories id
    url = base_address + '/categories/all-categories'
    res = session.get(url + '?with_sub=false')
    return [x for x in res.json() if x['categories_name'] == name_cat][0]['categories_id']

def create_sub_categories(id_cat: int, name_sub_cat: str):
    # create sub categories
    url = base_address + '/sub-categories/create'
    res = session.post(url,
        json={'name': name_sub_cat, 'category_id': id_cat},
        headers={'X-CSRF-TOKEN': csrf_access_token}
    )
    console.log('[green]sub-categories [blue]{}[/blue] complete[/green], message: {}'.format(
        name_sub_cat,res.json()['detail'])
    )
    sleep(1)
    # get sub categories id
    url = base_address + '/categories/all-categories?with_sub=true'
    res = session.get(url)
    return [
        x for x in res.json() if x['sub_categories_name'] == name_sub_cat and x['categories_id'] == id_cat
    ][0]['sub_categories_id']

def create_item_sub_categories(id_sub_cat: int, name_item_sub: str):
    # create item sub
    url = base_address + '/item-sub-categories/create'
    res = session.post(url,
        json={'name': name_item_sub, 'sub_category_id': id_sub_cat},
        headers={'X-CSRF-TOKEN': csrf_access_token}
    )
    console.log(
        '[green]item-sub-categories [blue]{}[/blue] complete[/green], message: {}'.format(
            name_item_sub,res.json()['detail'])
    )
    sleep(1)

def create_variants(variant_data: dict, name_product: str) -> str:
    url = base_address + '/variants/create-ticket'
    res = session.post(url, json=variant_data, headers={'X-CSRF-TOKEN': csrf_access_token})
    console.log(
        '[green]variants [blue]{}[/blue] complete[/green], message: {}'.format(
            name_product,res.json().get('detail') or res.json().get('ticket')
        )
    )
    sleep(1)
    return res.json().get('ticket')

def create_products(ticket: str, product_data: dict):
    url = base_address + '/products/create'
    product_data['ticket_variant'] = ticket
    files = [("image_product", (f"{x}.jpeg", open(f'images/{x}.jpeg','rb'),"image/jpeg")) for x in range(1,6)]
    if product_data['name'] == 'PAULMAY Sepatu Formal Pria Modena 01 - Hitam' or product_data['name'] == 'IPHONE XR ':
        [files.append(("image_variant", (f"{x}.jpeg", open(f'images/{x}.jpeg','rb'),"image/jpeg"))) for x in range(1,3)]

    res = session.post(url,
        data=product_data,
        files=files,
        headers={'X-CSRF-TOKEN': csrf_access_token}
    )
    console.log(
        '[green]products [blue]{}[/blue] complete[/green], message: {}'.format(product_data['name'],res.json()['detail'])
    )
    sleep(1)


if __name__ == '__main__':
    with console.status("[bold green]Working on tasks...") as status:
        login()
        create_brands()

        with open('category.json') as f:
            category_data = json.loads(f.read())

        for category in category_data:
            id_cat = create_categories(category['name_category'])
            for sub_category in category['sub_categories']:
                id_sub_cat = create_sub_categories(id_cat,sub_category['name_sub_category'])
                for item_sub_category in sub_category['item_sub_categories']:
                    create_item_sub_categories(id_sub_cat,item_sub_category['name_item_sub_category'])

        with open('products.json') as f:
            product_data = json.loads(f.read())

        for product in product_data:
            ticket = create_variants(product['variant'],product['product_data']['name'])
            create_products(ticket,product['product_data'])
