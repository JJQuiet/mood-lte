import os, csv
from account.models import Docitems, Document, editRecord
from mood import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
# Create your views here.
def index(request):
    context = {
        'content_template': 'components/default.html',
    }
    return render(request, 'account/starter.html', context)

def manual_label(request):
    if request.POST:# 用来判断fileupload
        newdoc = Document.objects.create(file=request.FILES['docfile'], uploader=request.user)
        file = os.path.join(settings.MEDIA_ROOT, 'csv', request.FILES['docfile'].name)
        with open(file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for record in reader:
                Docitems.objects.create(document=newdoc, review=record[1])
    context = {
        "documents": Document.objects.all(),
        'content_template': 'components/manual_label.html',
        'card_alert_display': 'd-none',
        'edit_alert_display': 'd-none',
        'process_alert_display': 'd-none'
    }
    return render(request, 'pages/manual_label_page.html', context)

def file_download(request, docfile):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filename.csv"'
    writer = csv.writer(response)
    writer.writerow(['calculabel','review','last_edit_time','label1', 'label2', 'label3'])
    data = Docitems.objects.filter(document__id=docfile)
    for row in data:
        rowobj = [row.calculabel(), row.review, row.last_edit_time, row.label1, row.label2, row.label3]
        writer.writerow(rowobj)
    return response
    

def edit(request):
    data = {}
    selectedDoc = Document.objects.get(id=request.POST['selectedFile'])
    edit_record = editRecord.objects.filter(editor=request.user, file=selectedDoc).first()
    if edit_record:
        data['total'] = Docitems.objects.filter(document=selectedDoc).count()
        data['already'] = Docitems.objects.filter(document=selectedDoc, id__lte=request.POST['cur_edit_row']).count()
        edit_record_row = edit_record.last_edit_row
        cur_edit = Docitems.objects.get(id=edit_record_row)
        data['cur_edit_id'] = cur_edit.id
        data['cur_edit_review'] = cur_edit.review
    else:
        if editRecord.objects.filter(file=selectedDoc).count() >= 3:
            data['edit_alert_display'] = 'd-block'
        else:
            cur_edit = Docitems.objects.filter(document__id=request.POST['selectedFile']).first()
            editRecord.objects.create(file=selectedDoc, editor=request.user, last_edit_row=cur_edit.id)
            data['cur_edit_id'] = cur_edit.id
            data['cur_edit_review'] = cur_edit.review
            data['total'] = Docitems.objects.filter(document=selectedDoc).count()
            data['already'] = 1
    return JsonResponse(data)

def previous(request):
    data = {}
    selectedDoc = Document.objects.get(id=request.POST['selectedFile'])
    first = Docitems.objects.filter(document=selectedDoc).first().id
    if int(request.POST['cur_edit_row']) == first:
        data['process_alert_display'] = 'd-block'
    else:
        editRecord.objects.filter(editor=request.user, file=selectedDoc).update(last_edit_row=int(request.POST['cur_edit_row'])-1)
        data['cur_edit_review'] = Docitems.objects.get(id=int(request.POST['cur_edit_row'])-1).review
        data['total'] = Docitems.objects.filter(document=selectedDoc).count()
        data['already'] = Docitems.objects.filter(document=selectedDoc, id__lte=request.POST['cur_edit_row']).count()-1
    return JsonResponse(data)

def next_(request):
    data = {}
    selectedDoc = Document.objects.get(id=request.POST['selectedFile'])
    last = Docitems.objects.filter(document=selectedDoc).last().id
    if int(request.POST['cur_edit_row']) == last:
        data['process_alert_display'] = 'd-block'
    else:
        editRecord.objects.filter(editor=request.user, file=selectedDoc).update(last_edit_row=int(request.POST['cur_edit_row'])+1)
        data['cur_edit_review'] = Docitems.objects.get(id=int(request.POST['cur_edit_row'])+1).review
        data['total'] = Docitems.objects.filter(document=selectedDoc).count()
        data['already'] = Docitems.objects.filter(document=selectedDoc, id__lte=request.POST['cur_edit_row']).count()+1
    return JsonResponse(data)

def next_senti(request):
    data = {}
    selectedDoc = Document.objects.get(id=request.POST['selectedFile'])
    last = Docitems.objects.filter(document=selectedDoc).last().id
    if int(request.POST['cur_edit_row']) == last:
        data['process_alert_display'] = 'd-block'
    else:
        editRecord.objects.filter(editor=request.user, file=selectedDoc).update(last_edit_row=int(request.POST['cur_edit_row'])+1)
        data['cur_edit_review'] = Docitems.objects.get(id=int(request.POST['cur_edit_row'])+1).review
        data['total'] = Docitems.objects.filter(document=selectedDoc).count()
        data['already'] = Docitems.objects.filter(document=selectedDoc, id__lte=request.POST['cur_edit_row']).count()+1
        if Docitems.objects.get(id=request.POST['cur_edit_row']).editor1 in [None, request.user.username]:
            Docitems.objects.filter(Q(id=request.POST['cur_edit_row']), Q(editor1=None) | Q(editor1=request.user.username) ).update(editor1=request.user.username, label1=request.POST['sentiValue'])
        elif Docitems.objects.get(id=request.POST['cur_edit_row']).editor2 in [None, request.user.username]:
            Docitems.objects.filter(Q(id=request.POST['cur_edit_row']), Q(editor2=None) | Q(editor2=request.user.username)).update(editor2=request.user.username, label2=request.POST['sentiValue'])
        elif Docitems.objects.get(id=request.POST['cur_edit_row']).editor3 in [None, request.user.username]:
            Docitems.objects.filter(Q(id=request.POST['cur_edit_row']), Q(editor3=None) | Q(editor3=request.user.username)).update(editor3=request.user.username, label3=request.POST['sentiValue'])
    return JsonResponse(data)

