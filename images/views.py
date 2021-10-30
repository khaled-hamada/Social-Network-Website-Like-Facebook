from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse


from common.decorators import ajax_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from common.decorators import ajax_required
from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action, redis_connect

# Create your views here.
r = redis_connect()
@login_required
def image_create(request):
    if request.method == "POST":
        form = ImageCreateForm(data = request.POST)
        #form is submitted from user
        if form.is_valid():
            # create a new instance but do not save to associate user to it
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image',new_item )
            messages.success(request,"Image added successfully" )
            return redirect(new_item.get_absolute_url())

    else:
        #build form with the provided get request title and url
        form = ImageCreateForm(data = request.GET)
    
    return render(request, 'images/image/create.html',{'section':'images', 'form':form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    #increment total image views by 1
    total_views = r.incr(f'imge:{image.id}:views')
    #increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    return render(request,
     'images/image/detail.html',
      {'section':'images',
       'total_views': total_views,
        'image':image})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:  # unlike
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:  # fail silently
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images= Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an interger deliver the first page
        image = paginator.page(1)
    except  EmptyPage:
        if request.is_ajax():
            #if the request is an ajax , so have reahed the end
            #return an empty page to stop the ajax requests
            return HttpResponse('')
        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    

    if request.is_ajax():
        return render(request,
                     'images/image/list_ajax.html',
                     {
                        'section':'images',
                        'images':images,
                     })
    #default http requests
    return render(request,
                'images/image/list.html',
                 {
                        'section':'images',
                        'images':images,
                 })


@login_required
def image_ranking(request):
   # get image ranking dictionary
    print(r.zrange('image_ranking', 0, -1))
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # get most viewed images
    most_viewed = list(Image.objects.filter(
        id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images',
                   'most_viewed': most_viewed})
