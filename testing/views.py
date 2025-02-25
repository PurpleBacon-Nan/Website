from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import FishStock,MoneyStock,FishStockLog,Space,MoneyStockLog
from .forms import AddUnitsForm, RemoveUnitsForm,AddMoney,RemoveMoney,AddFishForm,DeleteFishForm
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


# Create your view here.

def home(response):
    return render(response,"main/base.html",{})

def about(response):
    return render(response,"main/About.html",{})

@login_required
def clear_fish_log(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to perform this action.")

    FishStockLog.objects.all().delete()
    return HttpResponseRedirect('/fishlist/')


@login_required
def clear_money_log(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to perform this action.")

    MoneyStockLog.objects.all().delete()
    return HttpResponseRedirect('/balance/')

@login_required()
def balance(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")

    day = request.GET.get('day', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)

    logs = MoneyStockLog.objects.all().order_by('-timestamp')

    if day:
        logs = logs.filter(timestamp__day=day)
    if month:
        logs = logs.filter(timestamp__month=month)
    if year:
        logs = logs.filter(timestamp__year=year)




    balance = MoneyStock.objects.first()
    add_money_form = AddMoney()
    remove_money_form = RemoveMoney()
    logs = MoneyStockLog.objects.all().order_by('-timestamp')


    if request.method == "POST":
        if "add_money" in request.POST:
            add_money_form = AddMoney(request.POST)
            remove_money_form = RemoveMoney()
            if add_money_form.is_valid():
                add_amount = add_money_form.cleaned_data['balance']
                money_stock, _ = MoneyStock.objects.get_or_create(id=1, defaults={'balance': 0})
                money_stock.balance += add_amount
                money_stock.save()

                MoneyStockLog.objects.create(
                    balance=money_stock,
                    action="add",
                    amount=add_amount,
                    timestamp=timezone.now()
                )
                return HttpResponseRedirect('/balance/')
            else:
                add_money_form = AddMoney()

    if request.method == "POST":
        if "remove_money" in request.POST:
            add_money_form = AddMoney()
            remove_money_form = RemoveMoney(request.POST)
            if remove_money_form.is_valid():
                remove_amount = remove_money_form.cleaned_data['balance']
                money_stock, _ = MoneyStock.objects.get_or_create(id=1, defaults={'balance': 0})
                if money_stock.balance >= remove_amount:
                    money_stock.balance -= remove_amount
                    money_stock.save()

                MoneyStockLog.objects.create(
                    balance=money_stock,
                    action="remove",
                    amount=remove_amount,
                    timestamp=timezone.now()
                )
                return HttpResponseRedirect('/balance/')
            else:
                remove_money_form.add_error('amount', 'Not enough money to remove.')






    return render(request, "main/balance.html",{
        'balance':balance,
        'logs':logs,
        'add_money_form': add_money_form,
        'remove_money_form': remove_money_form,
        'day': day,
        'month': month,
        'year': year})


@login_required
def fish_list_view(request,space_id=None):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")

    day = request.GET.get('day', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)

    fishes = []
    add_form = AddUnitsForm()
    remove_form = RemoveUnitsForm()
    spaces = Space.objects.all()
    space = None
    add_fish_form = AddFishForm()
    delete_fish_form = DeleteFishForm()

    if space_id:
        space = get_object_or_404(Space, id=space_id)
        fishes = FishStock.objects.filter(space=space)
        logs = FishStockLog.objects.filter(fish__space=space).order_by('-timestamp')
    else:
        space = None
        fishes = FishStock.objects.all()
        logs = FishStockLog.objects.all().order_by('-timestamp')

    if day:
        logs = logs.filter(timestamp__day=day)
    if month:
        logs = logs.filter(timestamp__month=month)
    if year:
        logs = logs.filter(timestamp__year=year)



    add_form = AddUnitsForm(space=space)
    remove_form = RemoveUnitsForm(space=space)

    if request.method == "POST":
        if "add_fish" in request.POST:
            add_fish_form = AddFishForm(request.POST)
            if add_fish_form.is_valid():
                add_fish_form.save()

                return HttpResponseRedirect(f'/fishlist/{space.id}/' if space else '/fishlist/')

        if "add" in request.POST:
            add_form = AddUnitsForm(request.POST,space=space)
            remove_form = RemoveUnitsForm()
            if add_form.is_valid():
                selected_fish = add_form.cleaned_data['fish']
                added_units = add_form.cleaned_data['quantity']
                selected_fish.quantity += added_units
                selected_fish.save()

                FishStockLog.objects.create(
                    fish=selected_fish,
                    action="add",
                    quantity=added_units,
                    timestamp=timezone.now()
                )
                return HttpResponseRedirect(f'/fishlist/{space.id}/' if space else '/fishlist/')

        if "remove" in request.POST:
            add_form = AddUnitsForm()
            remove_form = RemoveUnitsForm(request.POST,space=space)
            if remove_form.is_valid():
                selected_fish = remove_form.cleaned_data['fish']
                removed_units = remove_form.cleaned_data['quantity']
                if selected_fish.quantity >= removed_units:
                    selected_fish.quantity -= removed_units
                    selected_fish.save()
                    FishStockLog.objects.create(
                        fish=selected_fish,
                        action="remove",
                        quantity=removed_units,
                        timestamp=timezone.now()  # Automatically adds the current time
                    )
                else:
                    remove_form.add_error('quantity', 'Not enough units to remove.')
                return HttpResponseRedirect (f'/fishlist/{space.id}/'if space else '/fishlist/')

        if "delete_fish" in request.POST:
            delete_fish_form = DeleteFishForm(request.POST)
            if delete_fish_form.is_valid():
                selected_fish = delete_fish_form.cleaned_data['fish']
                selected_fish.delete()
                return HttpResponseRedirect(f'/fishlist/{space.id}/' if space else '/fishlist/')
        else:
            delete_fish_form = DeleteFishForm()

    spaces = Space.objects.all()



    return render(request, 'main/Fishes.html', {'fishes': fishes,'add_form': add_form, 'remove_form': remove_form, 'logs':logs,'space': space, 'spaces': spaces,'day': day,'month': month,'year': year,'add_fish_form': add_fish_form,'delete_fish_form':delete_fish_form})
