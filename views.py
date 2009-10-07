# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect

from lib import render_to

def context_processor(request):
    return {'user': request.user, 'debug': settings.DEBUG}

def is_valid_user(user):
    return user.is_authenticated()

def check_session(request):
    dur = timedelta(minutes=settings.SESSION_DURATION)
    now = datetime.now()
    ses = request.session.get('logged_timestamp', None)
    request.session['logged_timestamp'] = now
    request.session.modified = True
    return (ses and now - ses < dur)
    
@render_to('login.html', context_processor)
def login(request):
    from forms import Login
    if is_valid_user(request.user):
        if 'logged_timestamp' in request.session:
            del(request.session['logged_timestamp'])
        auth.logout(request)
        request.session.set_test_cookie()
        return HttpResponseRedirect('/login/')

    context = {
        'page_title': _(u'Login page')
        'session_duration': settings.SESSION_DURATION
        }

    if request.session.test_cookie_worked():
        if request.method == 'POST':
            form = Login(request.POST, error_class=DivErrorList)
            context.update( {'form': form} )
            if form.is_valid():
                login = form.cleaned_data.get('login', None)
                passwd = form.cleaned_data.get('passwd', None)
                
                user = auth.authenticate(username=login, password=passwd)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/logged/')
                else:
                    context = {'error_desc': _(u'Probably, you made a mistake.')}
            else:
                context = {'error_desc': _(u'Form is not valid.')}
        else:
            context.update( {'form': Login()} )
        return context
    else: # cookie ещё не установлен
        return HttpResponseRedirect('/')

@user_passes_test(is_valid_user, login_url='/')
def logout(request):
    if 'logged_timestamp' in request.session:
        del(request.session['logged_timestamp'])
    auth.logout(request)
    sout = request.GET.get('session', None)
    if sout and sout == 'out':
        return HttpResponseRedirect('/sessionout/')
    else:
        return HttpResponseRedirect('/')

@user_passes_test(is_valid_user, login_url='/')
def logged(request):
    request.session['logged_timestamp'] = datetime.now()
    request.session.modified = True

    stat = UsageStat(user=request.user)
    stat.save()

    all_groups = request.user.groups.all()

    # Если у пользователя выставлен флаг "Изменить пароль", заставляем
    # его это сделать.

    if request.user.change_password == 1:
        return HttpResponseRedirect('/password/')

    # Если зашёл представитель или администратор организации, у
    # которой просрочен срок регистрации, то отправляем его
    # регистрироваться повторно.

    def org_is_valid(request):
        return getattr(settings, 'CHECK_ORG_VALIDATION', False) and \
            request.user.organization.srd_data is not None and \
            request.user.organization.srd_data < datetime.now()

    if 'User' in [a.name for a in all_groups]:
        if org_is_valid(request):
            return HttpResponseRedirect('/orgexpired/')
        return HttpResponseRedirect('/invite/')
    elif 'OrgAdmin' in [a.name for a in all_groups]:
        if org_is_valid(request):
            return HttpResponseRedirect('/orgexpired/')
        return HttpResponseRedirect('/manager/')
    elif 'Manager' in [a.name for a in all_groups]:
        return HttpResponseRedirect('/manager/')
    elif 'Boss' in [a.name for a in all_groups]:
        return HttpResponseRedirect('/manager/')
    else:
        return HttpResponseRedirect('/logout/')

@render_to('message.html', context_processor)
def sessionout(request):
    return {'message_title': 'Время сессии истекло',
            'message_desc': 'Необходимо повторно пройти процесс регистрации пользователя в системе.'}
