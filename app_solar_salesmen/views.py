from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import sqlite3 as sql
import pandas as pd
import plotly.express as px

def login(request):
    if request.method =="GET":
        return render(request, "login.html")
    else:
        username=request.POST.get('username')
        senha=request.POST.get('senha')
        
        user=authenticate(username=username, password=senha)

        if user:
            login_django(request, user)
            return redirect('')
        else:
            messages.error(request, 'Username ou senha invalidos')
            return render(request, 'login.html')
        

def cadastro(request):
    if request.method=='GET':
        return render(request, "cadastro.html")
    else:
        email=request.POST.get('email')
        username=request.POST.get('username')
        senha=request.POST.get('senha')
        confirmar_senha=request.POST.get('confirmar_senha')
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem!")
            return render(request, "cadastro.html")
        
        if User.objects.filter(username=username).first():
            messages.error(request,'Já existe um usuário com esse username')
            return render(request, "cadastro.html")
        user=User.objects.create_user(username=username, email=email, password=senha)
        user.save()

        return redirect('login')

def table_append(request):
    if request.method == "POST":
        id_produto = int(request.POST.get('selection'))
        qtd = int(request.POST.get('qtd'))
        connection = sql.connect('db.sqlite3')
        cursor = connection.cursor()
        cursor.execute("""
        SELECT valor
        FROM produtos 
        WHERE id = %s
        """, [id_produto])
        valor = cursor.fetchone()[0]
        fat = valor * qtd
        id_vendedor = request.user.id
        cursor.execute("""
        INSERT INTO vendas (id_p, id_v, qtd, fat)
        VALUES (%s, %s, %s, %s)
        """, [id_produto, id_vendedor, qtd, fat])
        connection.close()
        return redirect('table_append')

def makegraph(request):
    connection = sql.connect('db.sqlite3')
    cursor = connection.cursor()
    if request.method == "POST":
        graphtype = request.POST.get('graphtype')
        if graphtype == 'bar':
            cursor.execute('''
                 SELECT u.nome, p.nome, v.qtd, v.fat
                 FROM vendas v
                 JOIN auth_user u ON v.id_v = u.id
                 JOIN produtos p ON v.id_p = p.id
                 ''')
            rows = cursor.fetchall()
            connection.close()
            df = pd.DataFrame(rows, columns=['vendedor', 'produto', 'qtd', 'fat'])
            eixo_x_col = request.POST.get('eixo_x') # <option name="eixo_x" value="id_v"> <option name="eixo_x" value="id_p" >
            y = request.POST.get('eixo_y') # <option name="eixo_y" value="qtd"> <option name="eixo_y" value="fat">
            if eixo_x_col == "id_v":
                x = 'vendedor'
                colors = 'produto'
            else:
                x = 'produto'
                colors = 'vendedor'
            fig = px.bar(df, x=x, y=y, color=colors)
            fig = fig.to_html(full_html=False)
        elif graphtype == 'pie':
            cursor.execute('''
                SELECT u.nome, p.nome, v.qtd, v.fat
                FROM vendas v
                JOIN auth_user u ON v.id_v = u.id
                JOIN produtos p ON v.id_p = p.id
                ''')
            rows = cursor.fetchall()
            connection.close()
            df = pd.DataFrame(rows, columns=['vendedor', 'produto', 'qtd', 'fat'])
            names = request.POST.get('names') # vendedor ou produto
            values = request.POST.get('values') # quantidade ou faturamento
            fig = px.pie(df, names=names, values=values)