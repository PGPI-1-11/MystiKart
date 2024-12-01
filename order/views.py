from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from django.contrib import messages

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    state_map = [
        (1, 'Procesado'),
        (2, 'Enviado'),
        (3, 'Completado'),
    ]
    order_progress = {
        'procesado': 1,
        'enviado': 2,
        'completado': 3,
    }.get(order.status, 0)

    return render(request, 'orderStatus.html', {
        'order': order,
        'order_progress': order_progress,
        'state_map': state_map,
    })



def order_search(request):
    tracking_id = request.GET.get('id_tracking')  
    if tracking_id:
        try:
            order = Order.objects.get(id_tracking=tracking_id)
            state_map = [
                (1, 'Procesado'),
                (2, 'Enviado'),
                (3, 'Completado'),
            ]
            order_progress = {
                'procesado': 1,
                'enviado': 2,
                'completado': 3,
            }.get(order.status, 0)

            return render(request, 'orderStatus.html', {
                'order': order,
                'order_progress': order_progress,
                'state_map': state_map,
            })
        except Order.DoesNotExist:
            messages.error(request, 'El ID de seguimiento no existe.')
            return redirect('home')  

