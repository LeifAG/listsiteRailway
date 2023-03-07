from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .forms import UserRegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from .models import List, Object, SharedList
from django.contrib import messages
from django.contrib.auth.models import User

def registrera(request):
    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            anvandarnamn = form.cleaned_data.get('username')
            messages.success(request, f'Konto skapades för {anvandarnamn}')
            return redirect('loggain')
    else:
        form=UserRegisterForm()

    return render(request, 'listapp/registrera.html',{'form':form})

class AllaListor(LoginRequiredMixin,ListView):
    model=List
    template_name = 'listapp/hem.html'
    context_object_name = 'listor'
    ordering = ['-cdate']

    def get_queryset(self):
        user = self.request.user
        # Get lists created by the user or shared with the user
        queryset = List.objects.filter(cuser=user) | List.objects.filter(sharedlist__user=user)
        # Distinct to remove duplicates
        return queryset.distinct()



class EnLista(LoginRequiredMixin,ListView):
    model=Object
    template_name = 'listapp/lista.html'
    context_object_name = 'objects'

    def get_queryset(self):
        return Object.objects.filter(list=self.kwargs['pk'])

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['listan'] = get_object_or_404(List, id=self.kwargs['pk'])
        return context
    
    def post(self, request, *args, **kwargs):
            obj = get_object_or_404(Object, pk=request.POST.get('object_id'))
            obj.purchased = not obj.purchased
            obj.save()
            return redirect('lista-sida', pk=self.kwargs['pk'])

class SkapaLista(LoginRequiredMixin,CreateView):
    model=List
    fields=['listname']

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['status'] = {"status":"Ny"}
        return context

    def form_valid(self,form):
        form.instance.cuser=self.request.user
        return super().form_valid(form)

class UppdateraLista(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=List
    fields=['listname']

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['status'] = {"status":"Uppdatera"}
        return context

    def test_func(self):
        user = self.request.user
        lista = get_object_or_404(List, pk=self.kwargs['pk'])
        return user == lista.cuser

class RaderaLista(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=List
    success_url='/'

    def test_func(self):
        user = self.request.user
        lista = get_object_or_404(List, pk=self.kwargs['pk'])
        return user == lista.cuser

class SkapaObject(LoginRequiredMixin,CreateView):
    model=Object
    fields=['objectname', 'amount']

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        lista=get_object_or_404(List,id=self.kwargs.get('l_pk'))
        context['status'] = {"status":"Ny",'listID':lista.id}
        return context

    def form_valid(self,form):
        form.instance.list=get_object_or_404(List,id=self.kwargs.get('l_pk'))
        return super().form_valid(form)

class UppdateraObject(LoginRequiredMixin,UpdateView):
    model=Object
    fields=['objectname', 'amount']

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['status'] = {"status":"Uppdatera"}
        return context

class RaderaObject(LoginRequiredMixin,DeleteView):
    model=Object

    def get_success_url(self):
        lista = self.object.list
        return reverse_lazy('lista-sida', kwargs={'pk':lista.id})

class RaderaPurchasedObject(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'listapp/confirm_delete_purchased.html'

    def get_success_url(self):
        lista = get_object_or_404(List, id=self.kwargs.get('l_pk'))
        return reverse_lazy('lista-sida', kwargs={'pk': lista.id})

    def test_func(self):
        user = self.request.user
        list_pk = self.kwargs['l_pk']
        lista = get_object_or_404(List, pk=list_pk)
        return user == lista.cuser

    def get(self, request, *args, **kwargs):
        context = {}
        list_pk = self.kwargs.get('l_pk')
        objects_to_delete = Object.objects.filter(list__pk=list_pk, purchased=True)
        if not objects_to_delete.exists():
            messages.warning(request, 'Det finns inga markerade artiklar att radera.')

            return HttpResponseRedirect(reverse_lazy('lista-sida', kwargs={'pk': list_pk}))
        context['objects'] = objects_to_delete
        context['lista'] = {'listID': list_pk}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        list_pk = self.kwargs.get('l_pk')
        objects_to_delete = Object.objects.filter(list__pk=list_pk, purchased=True)
        objects_to_delete.delete()
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)
    


class SharedListCreateView(LoginRequiredMixin, CreateView):
    model = SharedList
    fields = ['email']

    def get_success_url(self):
        return reverse_lazy('lista-sida', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            form.instance.user = user
            form.instance.list = List.objects.get(pk=self.kwargs['pk'])  # Set the list field
            return super().form_valid(form)
        except User.DoesNotExist:
            form.add_error('email', f'No user found with email address {email}.')
            return self.form_invalid(form)