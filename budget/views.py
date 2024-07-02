from django.shortcuts import render,redirect

from django.views.generic import View

from budget.forms import ExpenseModelForm,IncomeModelForm,RegistrationForm,LoginForm,SummaryForm

from budget.models import Expense,Income

from django.contrib import messages

from django.utils import timezone

from django.db.models import Sum

from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout

from budget.decorators import signin_required

from django.utils.decorators import method_decorator

import datetime


# Create your views here.

@method_decorator(signin_required,name="dispatch")
class ExpenseCreateView(View):

    def get(self,request,*args,**kwargs):

        form_instance=ExpenseModelForm()

        # qs=Expense.objects.all() # query for fetching all expenses
        
        qs=Expense.objects.filter(user_object=request.user) #logined user expense only

        return render(request,"expense_create.html",{"form":form_instance,"data":qs})
    
    def post(self,request,*args,**kwargs):

        form_instance=ExpenseModelForm(request.POST)

        if form_instance.is_valid():

            # adding user_object to form_instance before saving form_instance
            form_instance.instance.user_object=request.user

            form_instance.save() #we creating expense object missing user_object

            # data=form_instance.cleaned_data
            # Expense.objects.create(**data,user_object=request.user)

            messages.success(request,"expense created!!")
           
            # return redirect("expense-create")
            print("Expense has been created")
            return redirect("expense-add")
        
        else:

            messages.error(request,"expense not created")

            return render(request,"expense_create.html",{"form":form_instance})

@method_decorator(signin_required,name="dispatch")
class ExpenseUpdateView(View):

    def get(self,request,*args,**kwargs):
        

        id=kwargs.get("pk")

        expense_object=Expense.objects.get(id=id)

        form_instance=ExpenseModelForm(instance=expense_object)

        return render(request,"expense_update.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        expense_object=Expense.objects.get(id=id)

        form_instance=ExpenseModelForm(instance=expense_object,data=request.POST)

        if form_instance.is_valid():

            form_instance.save()

            messages.success(request,"expense updated")

            return redirect("expense-create")
        
        else:

            messages.error(request,"expense not updated")

            return render(request,"expense_update.html",{"form":form_instance})

@method_decorator(signin_required,name="dispatch")
class ExpenseDetailView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Expense.objects.get(id=id)

        return render(request,"expense_detail.html",{"data":qs})

@method_decorator(signin_required,name="dispatch")
class ExpenseDeleteView(View):

    def get(self,request,*args,**kwargs):

        
        id=kwargs.get("pk")

        Expense.objects.get(id=id).delete()

        messages.success(request,"expense deleted")

        return redirect("expense-create")


@method_decorator(signin_required,name="dispatch")
class ExpenseSummaryView(View):


    def get(self,request,*args,**kwargs):

        current_month=timezone.now().month

        current_year=timezone.now().year

        expense_list=Expense.objects.filter(created_date__month=current_month,
                                            created_date__year=current_year,
                                            user_object=request.user
                                           )

        expense_total=expense_list.values("amount").aggregate(total=Sum("amount"))


        print(expense_total)

        category_summary=expense_list.values("category").annotate(total=Sum("amount"))

        print(category_summary)

        priority_summary=expense_list.values("priority").annotate(total=Sum("amount"))

        print(priority_summary)

        data={
            "expense_total":expense_total,

            "category_summary":category_summary,

            "priority_summary":priority_summary
        }



        return render(request,"expense_summary.html",data)

    
class IncomeCreateView(View):

    def get(self,request,*args,**kwargs):

        qs=Income.objects.all()

        form_instance=IncomeModelForm()

        return render(request,"income_create.html",{"form":form_instance,"data":qs})
    
    def post(self,request,*args,**kwargs):

        form_instance=IncomeModelForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.user_object=request.user

            form_instance.save()
            
            print("income has been created")

            messages.success(request,"income created")

            return redirect("income-add")
        
        else:

            messages.error(request,"income not created")

            return render(request,"income_create.html",{"form":form_instance})
        
class IncomeUpdateView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        income_object=Income.objects.get(id=id)

        form_instance=IncomeModelForm(instance=income_object)

        return render(request,"income_update.html",{"form":form_instance})
    
    def post(self,request,args,*kwargs):

        id=kwargs.get("pk")

        income_object=Income.objects.get(id=id)

        form_instance=IncomeModelForm(instance=income_object,data=request.POST)

        if form_instance.is_valid():

            form_instance.save()

            messages.success(request,"income updated")

            return redirect("income-create")
        
        else:

            messages.error(request,"income not updated")

            return render(request,"income_update.html",{"form":form_instance})



class IncomeDetailView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Income.objects.get(id=id)

        return render(request,"income_detail.html",{"data":qs})
    
class IncomeDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Income.objects.get(id=id).delete()

        messages.success(request,"income deleted")

        return redirect("income-create")

class IncomeSummaryView(View):

    def get(self,request,*args,**kwargs):


        current_month=timezone.now().month

        current_year=timezone.now().year

        income_list=Income.objects.filter(
          created_date__month=current_month,
          created_date__year=current_year,
          user_object=request.user

        )
        income_total=income_list.values("amount").aggregate(total=Sum("amount"))

        print(income_total)

        category_total=income_list.values("category").annotate(total=Sum("amount"))

        print(category_total)

        data={
            "income_total":income_total,
            "category_total":category_total
        }
        

        return render(request,"income_summary.html",data)
        

# registration
class SignUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,"register.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            # form_instance.save() password willnot be encrypted

            data=form_instance.cleaned_data

            User.objects.create_user(**data) #this will encrypt password

            print("user object created")

            return redirect("signin") #after successful registration will redirect to login

        else:
            print("user creation failed")

            return render(request,"register.html",{"form":form_instance})



# login

class SignInView(View):

    def get(self,request,*args,**kwargs):
        
        form_instance=LoginForm()
    
        return render(request,'login.html',{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            uname=data.get("username")

            pwd=data.get("password")

            user_object=authenticate(request,username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect("dashboard")

        messages.error(request,"invalid username or password")

        return render(request,'login.html',{"form":form_instance})

@method_decorator(signin_required,name="dispatch")
class SignOutView(View):

    def post(self,request,*args,**kwargs):

        logout(request)

        return redirect("sigin")


class DashBoardView(View):

    def get(self,request,*args,**kwargs):

        current_month=timezone.now().month

        current_year=timezone.now().year
        
        form_instance=SummaryForm()

        expense_list=Expense.objects.filter(user_object=request.user,created_date__month=current_month,created_date__year=current_year)

        income_list=Income.objects.filter(user_object=request.user,created_date__month=current_month,created_date__year=current_year)

        print("expense-list",expense_list)

        print("income-list",income_list)

        expense_total=expense_list.values('amount').aggregate(total=(Sum("amount")))

        income_total=income_list.values('amount').aggregate(total=(Sum("amount")))
        print(expense_total)
        print(income_total)

        monthly_expenses={}

        monthly_incomes={}

        for month in range(1,13):

            start_date=datetime.date(current_year,month,1)
            
            if month==12:

                end_date=datetime.date(current_year+1,1,1)

            else:
                
                end_date=datetime.date(current_year,month+1,1)
            
            monthly_expense_total=Expense.objects.filter(user_object=request.user,created_date__gte=start_date,created_date__lte=end_date).aggregate(total=Sum("amount"))['total']
            
            monthly_expenses[start_date.strftime('%B')]=monthly_expense_total if monthly_expense_total else 0

            monthly_income_total=Income.objects.filter(user_object=request.user,created_date__gte=start_date,created_date__lte=end_date).aggregate(total=Sum("amount"))['total']

            monthly_incomes[start_date.strftime('%B')]=monthly_income_total if monthly_income_total else 0

        print(monthly_expenses)

        print(monthly_incomes)

        return render(request,"dashboard.html",{"expense":expense_total,
                                                "income":income_total,
                                                "form":form_instance,
                                                "monthly_incomes":monthly_incomes,
                                                "monthly_expenses":monthly_expenses})

    def post(self,request,*args,**kwargs):

        form_instance=SummaryForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            start_date=data.get("start_date")

            end_date=data.get("end_date")

            expense_list=Expense.objects.filter(user_object=request.user,created_date_gte=start_date,created_date_lte=end_date)

            income_list=Income.objects.filter(user_object=request.user,created_date_gte=start_date,created_date_lte=end_date)

            print("expense-list",expense_list)
    
            print("income-list",income_list)
    
            expense_total=expense_list.values('amount').aggregate(total=(Sum("amount")))
    
            income_total=income_list.values('amount').aggregate(total=(Sum("amount")))
            print(expense_total)
            print(income_total)
    
            form_instance=SummaryForm()
            return render(request,"dashboard.html",{"expense":expense_total,"income":income_total,"form":form_instance})