var schedule_options = {
    allowCalEventOverlap : true,
    firstDayOfWeek : 1,
    region: 'center',
    buttons: false,
    resizable: function(calEvent, eventElement){
        return false;
    },
    eventRender : function(calEvent, $event) {
        var options = this.options;
        $event.css("backgroundColor", "#"+calEvent.color);
        $event.find('.time').css("backgroundColor", "#"+calEvent.color);
    },
    eventAfterRender: function(calEvent, $event){
        var options = this.options;
        var title = calEvent.start.format(options.timeFormat) + options.timeSeparator + calEvent.end.format(options.timeFormat);
        var content = calEvent.title;
        content += '<br/>'+calEvent.room_name;
        Ext.QuickTips.register({
            target: $event.find('div')[0],
            title: title,
            text: content,
            showDelay: 50,
            anchorToTarget: false
        });
        Ext.QuickTips.register({
            target: $event.find('div')[1],
            title: title,
            text: content,
            showDelay: 50
        });
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
                        type: 'POST',
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
                                $self.weekCalendar("updateEvent", data.obj);
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
    eventDrop: function(calEvent, callback, revert_callback){
        var $options = this.options;
        $.ajax({
            type: 'POST',
            url: $options.urls.change_date,
            dataType: 'json',
            data: {'start': (calEvent.start.getTime()/1000),
                   'pk': calEvent.id},
            error: function(){
                alert('Ошибка сервера. Обновите страницу.')
            },
            success: function(data){
                data.result && callback() || revert_callback();
            }
        });
    }
};