from django.shortcuts import render, HttpResponse, redirect
from apps.egg.models import *
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from djangounchained_flash import ErrorManager, ErrorMessage, getFromSession
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# Create your views here.

def index(request):
    print("Reloading *******")
    if 'count' in request.session:
        request.session['count']=request.session['count']
    else:
        request.session['count'] = 0
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
        request.session['count'] = len(Cart.objects.filter(user = user))
        # need to fix cart
        context = {
            'items':Item.objects.all(),
            'cart':Cart.objects.filter(user = user)
        }
        return render(request, 'egg/home.html', context)
    else: 
        context = {
            'items':Item.objects.all()
            # possible solution to page (1,2,3,etc) numbers
            # 'items':Item.objects.all().reverse().order_by('-id')[7:11]
        }
        return render(request, 'egg/home.html',context)

def loginorregister(request):
    if 'flash' not in request.session:
        request.session['flash'] = ErrorManager().addToSession()
    e = getFromSession(request.session['flash'])
    first_name_errors = e.getMessages('first_name')
    last_name_errors = e.getMessages('last_name')
    email_errors = e.getMessages('email')
    password_errors = e.getMessages('password')
    passc_errors = e.getMessages('passc')
    email2_errors = e.getMessages('email2')
    email_login_errors = e.getMessages('email_login')
    email2_login_errors = e.getMessages('email_login2')
    pass_login_errors = e.getMessages('pass_login2')
    request.session['flash'] = e.addToSession()
    context={
        'first_name_e':first_name_errors,
        'last_name_e':last_name_errors,
        'email_e': email_errors,
        'email2_e': email2_errors,
        'password_e':password_errors,
        'passc_e':passc_errors,
        'email_1':email_login_errors,
        'email_2':email2_login_errors,
        'pass_log':pass_login_errors
    }
    return render(request, 'egg/login.html', context)

def register(request):
    if request.method == 'POST':
        errors = User.objects.basic_validator(request.POST)
        e = getFromSession(request.session['flash'])
        if len(errors):
            for tag, error in errors.items():
                e.addMessage(error,tag)
            request.session['flash'] = e.addToSession()
            return redirect('/loginorregister')
        # need to add another vaidator for login
        print(request.POST)
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        conf = request.POST['passconf']
        hash1 = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        User.objects.create(first_name = first_name, last_name = last_name, email = email, password = hash1)
        user = User.objects.get(first_name = first_name, last_name = last_name, email = email, password = hash1)
        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['id']=user.id
        return redirect('/')
    else:
        return redirect('/')


def login(request):
    if request.method =='POST':
        email = request.POST['login_email']
        passw = request.POST['login_password']
        errors = User.objects.login_validator(request.POST)
        e = getFromSession(request.session['flash'])
        if len(errors):
            for tag, error in errors.items():
                e.addMessage(error, tag)
            request.session['flash'] = e.addToSession()
            return redirect('/loginorregister')

        user = User.objects.get(email = email)
        if bcrypt.checkpw(passw.encode(), user.password.encode()):
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            request.session['id']=user.id
            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

def itemDisplay(request,number):
    this_type = Item.objects.get(id=int(number)).item_type
    print('the type is')
    print(this_type)
    this_rating = float(Item.objects.get(id=int(number)).rating)
    print('float=')
    print(this_rating)
    stars=[]
    halfstar=[]
    while this_rating>=1:
        this_rating-=1
        stars.append(1)
    while this_rating>0:
        this_rating-=0.5
        halfstar.append(1)
    print(stars)
    print(halfstar)
    context={
        "item":Item.objects.get(id=int(number)),
        "similars":Item.objects.filter(item_type=this_type).exclude(id=int(number)),
        "stars":stars,
        "halfstar":halfstar
    }
    return render(request,'egg/item.html',context)


def create(request):
    if 'part' in request.POST and 'manuf' in request.POST and 'search_box' in request.POST:
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'), manufacturer__in=request.POST.getlist(u'manuf'), model_number__startswith=request.POST['search_box'])
        }
        
    elif 'part' in request.POST and 'search_box' in request.POST and 'manuf' not in request.POST :
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'), model_number__startswith=request.POST['search_box'])
        }
    elif 'manuf' in request.POST and 'search_box' in request.POST and 'part' not in request.POST :
        context = {
        'item':Item.objects.filter(manufacturer__in=request.POST.getlist(u'manuf'), model_number__startswith=request.POST['search_box'])
        }
    elif 'part' in request.POST and 'manuf' in request.POST and 'search_box' not in request.POST:
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'), manufacturer__in=request.POST.getlist(u'manuf'))
        }
    elif 'search_box' in request.POST and 'part' not in request.POST and 'manuf' not in request.POST:
        context = {
            'item':Item.objects.filter(model_number__startswith=request.POST['search_box'])
        }
    elif 'part' in request.POST and 'manuf' not in request.POST and 'search_box' not in request.POST:
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'))
        }
    elif 'manuf' in request.POST and 'part' not in request.POST and 'search_box' not in request.POST:
        context = {
        'item':Item.objects.filter(manufacturer__in=request.POST.getlist(u'manuf'))
        }
    else:
        return render(request, 'egg/filter.html', context = {'item':Item.objects.all()})
    return render(request, 'egg/filter.html', context)

def additem(request):
    
    if 'id' in request.session:
        request.session['count']+=1
        user = User.objects.get(id=request.session['id'])
        item = Item.objects.get(id = request.POST['item_id'])
        try:
            item = Item.objects.get(id = request.POST['item_id'])
            my_cart = Cart.objects.get(user = user, item = item)
            my_cart.quantity += 1
            my_cart.save()
        except:
            Cart.objects.create(user = user, item=item)
        return redirect('/cart')
    else:
        if 'cart' in request.session:
            request.session['count']+=1
            if 'item_id' not in request.POST:
                return HttpResponse('403 forbidden!')
            else:
                temp_cart = request.session['cart']
                temp_post = int(request.POST['item_id'])
                temp_cart.append(temp_post)
                request.session['cart'] = temp_cart
        else:
            if 'item_id' not in request.POST:
                return HttpResponse('403 forbidden!')
            else:
                request.session['count']+=1
                request.session['cart'] = []
                temp_cart = request.session['cart']
                temp_post = int(request.POST['item_id'])
                temp_cart.append(temp_post)
                request.session['cart'] = temp_cart
        return redirect('/cart')
        # need to ad logic here for session cart
    
def cart(request):
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
        total = 0
        for i in Cart.objects.filter(user=user):
            total += i.item.price * i.quantity
        context={
            "cart":Cart.objects.filter(user=user),
            'total':total
        }
    else:
        if 'cart' not in request.session:
            context = {
                'total':0
            }
            return render(request, 'egg/cart.html', context)
        else:    
            total = 0
            quant = {}
            for i in request.session['cart']:
                if i not in quant:
                    quant[i]=1
                else:
                    quant[i]+=1
                item = Item.objects.get(id=i)
                total += item.price
            
            for key, value in quant.items():
                key = int(key)
            context = {
                "cart" : Item.objects.filter(id__in=request.session['cart']),
                "total":total,
                "quant":quant
            }
    return render(request,'egg/cart.html',context)

def purchase(request):
    # print(request.POST)
    if 'id' in request.session:
        try:
            user = User.objects.get(id=request.session['id'])
            for i in Cart.objects.filter(user = user):
                OrderHistory.objects.create(user = user, item = i.item, quantity = request.POST[i.item.name])
                cart = Cart.objects.filter(item = i.item)
                request.session['count'] = 0
                cart.delete()
            return redirect('/orderhistory')
        except:
            return redirect('/')
    else:
        request.session['purchase'] = request.session['cart']
        request.session['count'] = 0
        del request.session['cart']
        return redirect('/orderhistory')

def orderhistory(request):
    if 'id' not in request.session:
        if 'purchase' not in request.session:
            return redirect('/')
        else:
            total = 0
            quant = {}
            for i in request.session['purchase']:
                if i not in quant:
                    quant[i]=1
                else:
                    quant[i]+=1
                item = Item.objects.get(id=i)
                total += item.price
            
            for key, value in quant.items():
                key = int(key)
            context = {
                "orderhis" : Item.objects.filter(id__in=request.session['purchase']),
                "total":total,
                "quant":quant
            }
            return render(request,'egg/orderhistory.html', context)
    else:
        user = User.objects.get(id=request.session['id'])
        total = 0
        for i in OrderHistory.objects.filter(user=user):
            total += i.item.price * i.quantity
            print(total)
        context = {
            'orderhis': OrderHistory.objects.filter(user=user),
            'total':total
        }
        return render(request,'egg/orderhistory.html', context)
    
def clear(request):
    if 'first_name' in request.session:
        del request.session['first_name']
    if 'last_name' in request.session:
        del request.session['last_name']
    if 'id' in request.session:
        del request.session['id']
    if 'cart' in request.session:
        del request.session['cart']
    if 'purchase' in request.session:
        del request.session['purchase']
    if 'count' in request.session:
        del request.session['count']
    return redirect('/')