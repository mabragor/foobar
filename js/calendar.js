//var dialog = $("#event_edit_container");
var options = {
    allowCalEventOverlap : true,
    firstDayOfWeek : 1,
    startParam: 'start',
    /*
    form: {
        dialog: dialog,
        startField: dialog.find("select[name='begin']"),
        roomField: dialog.find("select[name='room']"),
        courseField: dialog.find("select[name='course']"),
        formError: dialog.find('#form_error')
    },*/
    height : function(calendar) {
        return $(window).height() - $("h1").outerHeight();
    },
    resizable: function(calEvent, eventElement){
        return false;
    },
    eventRender : function(calEvent, $event) {
        $event.css("backgroundColor", "#"+calEvent.color);
    },
    eventNew : function(calEvent, $event) {
        var $self = this.element;
        var $options = this.options;
        var dialogContent = $("#event_edit_container");
        resetForm(dialogContent);

        var startField = dialogContent.find("select[name='begin']").val(calEvent.start);
        var roomField = dialogContent.find("select[name='room']");
        var courseField = dialogContent.find("select[name='course']");
        var formError = dialogContent.find('#form_error');

        dialogContent.dialog({
            modal: true,
            title: "New Calendar Event",
            close: function() {
                dialogContent.dialog("destroy");
                dialogContent.hide();
                $self.weekCalendar("removeUnsavedEvents");
            },
            buttons: {
                save : function(){
                    if (( ! roomField.val()) || ( ! courseField.val())){
                        formError.html('Заполните все поля!');
                    }else{
                        jQuery.ajax({
                            type: 'POST',
                            url: $options.urls.add_event,
                            dataType: 'json',
                            data: dialogContent.find('form').serialize(),
                            error: function(){
                                formError.html('Ошибка сервера!');
                            },
                            success: function(data){
                                if (data.error){
                                    formError.html(data.error);
                                }else{
                                    var event = data.obj;
                                    event.start = new Date(data.obj.start*1000);
                                    event.end = new Date(data.obj.end*1000);
                                    $self.weekCalendar("removeUnsavedEvents");
                                    $self.weekCalendar("updateEvent", event);
                                    dialogContent.dialog("close");
                                }
                            }
                        });
                    }
                },
                cancel : function(){
                    dialogContent.dialog("close");
                }
            }
        }).show();

        dialogContent.find(".date_holder").text($self.weekCalendar("formatDate", calEvent.start));
        setupStartAndEndTimeFields(startField, calEvent, $self.weekCalendar("getTimeslotTimes", calEvent.start));
        $(window).resize().resize(); //fixes a bug in modal overlay size ??
    },
    
    eventClick : function(calEvent, $event) {
        var $self = this.element;
        var $options = this.options;
        
        if(calEvent.readOnly) {
            return;
        }

        var dialogContent = $("#event_edit_container");
        resetForm(dialogContent);
        var startField = dialogContent.find("select[name='begin']").val($self.weekCalendar("formatDate", calEvent.start, 'Y-m-d H:i:s'));
        var roomField = dialogContent.find("select[name='room']").val(calEvent.room);
        var courseField = dialogContent.find("select[name='course']").val(calEvent.course);
        var formError = dialogContent.find('#form_error');
        dialogContent.find(".date_holder").text($self.weekCalendar("formatDate", calEvent.start));
        setupStartAndEndTimeFields(startField, calEvent, $self.weekCalendar("getTimeslotTimes", calEvent.start));

        dialogContent.dialog({
            modal: true,
            title: "Edit - " + calEvent.title,
            close: function() {
                dialogContent.dialog("destroy");
                dialogContent.hide();
                $self.weekCalendar("removeUnsavedEvents");
            },
            buttons: {
                save : function(){
                    jQuery.ajax({
                        type: 'GET',
                        url: $options.urls.add_event+calEvent.id+'/',
                        dataType: 'json',
                        data: dialogContent.find('form').serialize(),
                        error: function(){
                            formError.html('Ошибка сервера!');
                        },
                        success: function(data){
                            if (data.error){
                                formError.html(data.error);
                            }else{
                                var event = data.obj;
                                event.start = new Date(data.obj.start*1000);
                                event.end = new Date(data.obj.end*1000);
                                $self.weekCalendar("updateEvent", event);
                                dialogContent.dialog("close");
                            }
                        }
                    });
                },
                "delete" : function(){
                    jQuery.ajax({
                        type: 'POST',
                        url: $options.urls.del_event,
                        dataType: 'json',
                        data: {'id': calEvent.id},
                        error: function(){
                            formError.html('Ошибка сервера!');
                        },
                        success: function(data){
                            $self.weekCalendar("removeEvent", calEvent.id);
                            dialogContent.dialog("close");
                        }
                    });
                },
                cancel : function(){
                    dialogContent.dialog("close");
                }
            }
        }).show();
        $(window).resize().resize(); //fixes a bug in modal overlay size ??
    },
    eventDrop: function(calEvent, oldCalEvent, element){
        var $options = this.options;
        jQuery.ajax({
            type: 'POST',
            url: $options.urls.change_date,
            dataType: 'json',
            data: {'start': (calEvent.start.getTime()/1000),
                   'pk': calEvent.id},
            error: function(){
                alert('Ошибка сервера. Обновите страницу.')
            },
            success: function(data){
            }
        });
    }
};

function resetForm(dialogContent) {
    //FIXME
    dialogContent.find("select[name='room']").val('');
    dialogContent.find("select[name='course']").val('');
    dialogContent.find('#form_error').html('');
}

/*
 * Sets up the start and end time fields in the calendar event
 * form for editing based on the calendar event being edited
 */
function setupStartAndEndTimeFields($startTimeField, calEvent, timeslotTimes) {

    for(var i=0; i<timeslotTimes.length; i++) {
        var startTime = timeslotTimes[i].start;
        var startSelected = "";
        if(startTime.getTime() === calEvent.start.getTime()) {
            startSelected = "selected=\"selected\"";
        }

        $startTimeField.append("<option value=\"" + timeslotTimes[i].startValue + "\" " + startSelected + ">" + timeslotTimes[i].startFormatted + "</option>");
    }
}