from django.shortcuts import render
from django.views import generic

from ml.models import UserProfile, Publication, Resource


class GroupView(generic.ListView):
    template_name = 'group.html'
    context_object_name = 'users'

    def get_queryset(self):
        users = dict()
        try:
            users['leader'] = UserProfile.objects.get(membership='L')
        except UserProfile.DoesNotExist:
            pass
        users['members'] = list(UserProfile.objects.filter(
            membership='M'))
        users['exmembers'] = list(UserProfile.objects.filter(
            membership='X'))
        return users


def get_profile(request, username):
    context = {'user': UserProfile.objects.get(user__username=username)}
    return render(request, 'user.html', context)


class PublicationDetailView(generic.DetailView):
    template_name = 'publ_detail.html'
    model = Publication


class PublicationListView(generic.ListView):
    template_name = 'publ_list.html'
    context_object_name = 'publications'

    def get_queryset(self):
        return Publication.objects.order_by('-year')


class ResourceDetailView(generic.DetailView):
    template_name = 'res_detail.html'
    model = Resource


class ResourcesView(generic.ListView):
    template_name = 'res_list.html'
    context_object_name = 'resources'

    def get_queryset(self):
        return Resource.objects.order_by('name')


class IndexView(generic.TemplateView):
    template_name = 'ml_home.html'
