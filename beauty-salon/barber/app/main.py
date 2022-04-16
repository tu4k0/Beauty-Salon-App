import time

from flask import Flask, request, render_template, redirect, session
from flask_bootstrap import Bootstrap
import db
from forms import LoginForm, RegisterForm, OrderForm, StatusForm
app = Flask(__name__)

Bootstrap(app)


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        query = f"""
        SELECT * FROM Buser where login='{form.login.data}';
        """
        user = db.db_get(query)
        if not user:
            return redirect('/register')
        session['current_user'] = user
        session['current_user_cart'] = db.db_get(f"select * from cart where Buser_id={user['id']}")
        if session.get('current_user')['role_id'] == 1:
            return redirect('/manage_orders/1')
        return redirect('/')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['Get'])
def logout_view():
    session['current_user'] = None
    session['current_user_cart'] = None
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.db_get(f"""select * from Buser where login='{form.login.data}';""")
        if user:
            return render_template('register.html', form=form, alert='Юзер с таким логином уже существует'), 400
        query = f"insert into Buser (login, password, Role_id) values ('{form.login.data}', '{form.password.data}', 2);"
        db.db_save(query)
        user = db.db_get(f"""select * from Buser where login='{form.login.data}';""")
        session['current_user'] = user
        db.db_save(f"""insert into cart (Buser_id, Status_id) values ((SELECT MAX(id) FROM buser), 6);""")
        session['current_user_cart'] = db.db_get(f"""select * from cart where Buser_id=(SELECT MAX(id) FROM buser);""")
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def services():
    if not session.get('current_user'):
        return redirect('/login')
    query = """
    SELECT * FROM Service;
    """
    data = db.db_get(query, cur_type='all')
    return render_template('services.html', data=data)


@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    cart_id = session.get('current_user_cart')['id']
    query = f"""
    INSERT INTO Service_cart_rel (Service_id, Cart_id) VALUES ({item_id}, {cart_id})
    """
    db.db_save(query)
    return redirect('/')


@app.route('/view_cart', methods=['POST', 'GET'])
def view_cart():
    if not session.get('current_user') or not session.get('current_user_cart'):
        return redirect('/login')
    data = db.db_get(
        f"""select * from service where id in (select service_id  from Service_cart_rel where cart_id={session.get('current_user_cart')['id']});""",
        cur_type='all')
    price = 0
    if data:
        for item in data:
            price += item['price']
    context = {'data': data, 'price': price}
    return render_template('cart.html', data=context)


@app.route('/create_order', methods=['POST', 'GET', 'PATCH'])
def create_order():
    if not session.get('current_user'):
        return redirect('/login')
    form = OrderForm(request.form)
    price = request.args.get("price")
    user_id = session.get('current_user')['id']
    cart_id = session.get('current_user_cart')['id']
    if request.method == 'POST' and request.args.get("reject"):
        query = f"""update cart set status_id=7 where id={cart_id};
                     insert into cart (Buser_id, Status_id) values ({user_id}, 6);
                     insert into  border (Buser_id,Status_id,payment_type) values ({user_id}, 3, '{form.payment_type.data}');
                     insert into Order_cart_rel (Cart_id, Border_id) values ({cart_id},  (SELECT MAX(id) FROM border));"""
        db.db_save(query)
        session['current_user_cart'] = db.db_get(f'select * from cart where buser_id={user_id} and status_id=6;')
        return redirect('/rejected')
    elif request.method == 'POST' and price:
        query = f"""UPDATE Buser set name='{form.name.data}', last_name='{form.last_name.data}', surname='{form.surname.data}', phone='{form.phone.data}' where id={user_id};
                    update cart set status_id=7 where id={cart_id};
                    insert into cart (Buser_id, Status_id) values ({user_id}, 6);
                    insert into  border (Buser_id,Status_id,payment_type, time, price) values ({user_id}, 1, '{form.payment_type.data}', to_timestamp('{form.time.data}', 'yyyy-mm-dd hh24:mi:ss'), {price});
                    insert into Order_cart_rel (Cart_id, Border_id) values ({cart_id},  (SELECT MAX(id) FROM border));
"""
        db.db_save(query)
        session['current_user_cart'] = db.db_get(f'select * from cart where buser_id={user_id} and status_id=6;')
        return redirect('/success')
    data = db.db_get(
        f"""select * from service where id in (select service_id  from Service_cart_rel where cart_id={session.get('current_user_cart')['id']});""",
        cur_type='all')
    price = 0
    if data:
        for item in data:
            price += item['price']
    context = {'data': data, 'price': price}
    return render_template('order.html', data=context, form=form)


@app.route('/manage_orders/<int:status_id>', methods=['GET', 'POST'])
def manage_orders(status_id):
    if not session.get('current_user'):
        return redirect('/login')
    elif not session.get('current_user')['role_id'] == 1:
        return render_template('401.html')
    form = StatusForm(request.form)
    if request.method == 'POST':
        db.db_save(f'update border set Status_id={form.status.data} where id={request.args.get("ord_id")}')

    query = f"""
            select distinct o.id, o.buser_id, o.payment_type, o.time , u.name, u.last_name, u.surname, u.phone , s.sname, o.price from border o
    full outer join buser u on o.buser_id = u.id inner join cart c on u.id = c.buser_id inner join Order_cart_rel ok
        on o.id = ok.border_id and c.id=ok.cart_id inner join  Service_cart_rel r on r.cart_id = c.id inner join
    service s on r.service_id = s.id and r.cart_id = c.id where o.status_id={status_id} and c.status_id=7 order by id;
"""

    db_data = db.db_get(query, cur_type='all')
    data = prepare_data(db_data)
    return render_template('orders.html', data=data, form=form, status_id=status_id)


def prepare_data(data):
    res = []
    prev_id = None
    obj_ind = 0
    for item in data:
        if item['id'] == prev_id:
            res[obj_ind - 1]['services'].append(item['sname'] + ',')
            continue
        prev_id = item['id']
        obj_ind += 1
        res.append({
                    'id': item['id'],
                    'fio': f"{item['last_name']} {item['name']} {item['surname']}",
                    'phone': item['phone'],
                    'price': item['price'],
                    'time': item['time'],
                    'payment_type': item['payment_type'] + ',',
                    'services': [item['sname'], ]
        })
    return res


@app.route('/rejected', methods=['GET'])
def rejected():
    return render_template('rejected.html')


@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')


if __name__ == '__main__':
    db.create_db()
    time.sleep(5)
    db.fill_db()
    app.secret_key = 'super secret key'
    app.run(debug=True, host='0.0.0.0', port='8008')
