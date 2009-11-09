if (typeof(URLS) == 'undefined') URLS = {};
var schedule_options = {
    /** Must get from settings.py **/
    "timeslotHeight": 30,
    "timeslotsPerHour": 2,
    "overlapEventsSeparate": true,
    "businessHours": {"start": 8, "end": 18, "limitDisplay": true},
    /******************************/
    urls: URLS,
    data: function(start, end, callback, extra_data) {
        var $options = this.options;
        var data = {
            'start': Math.round(start.getTime()/1000),
            'end': Math.round(end.getTime()/1000)
        };
        data = jQuery.extend(data, extra_data);
        jQuery.ajax({
            type: 'POST',
            url: $options.urls.get_events,
            dataType: 'json',
            data: data,
            error: function(){
                alert('Ошибка сервера. Обновите страницу.')
            },
            success: callback
        });
    },
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
    eventDelete: function(calEvent){
        var $self = this;
        Ext.MessageBox.confirm(calEvent.title, 'Are you sure you want to delete event?', function(bt){
            if (bt == 'yes'){
                $.ajax({
                    type: 'POST',
                    url: $self.options.urls.del_event,
                    dataType: 'json',
                    data: {id: calEvent.id},
                    error: function(){
                        Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
                    },
                    success: function(data){
                        data.error && Ext.ux.msg('Failure', data.error, Ext.Msg.WARNING);
                        data.error || $self.removeEvent(calEvent.id);
                    }
                });
            }
        });
    },
    eventClick: function(calEvent, $calEvent, event){
        if (calEvent.start > new Date.now()){
            var ce_window = this.options.panel.ce_window;
            ce_window.show();
            ce_window.get(0).setValues({
                course_id: calEvent.course,
                start_date: calEvent.start,
                course_name: calEvent.title,
                event_id: calEvent.id
            });
        }

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
                Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
            },
            success: function(data){
                data.msg && Ext.ux.msg(data.msg, '', Ext.MessageBox.WARNING);
                data.result && callback() || revert_callback();
            }
        });
    },
    draggable: function(calEvent, $calEvent){
        return calEvent.start > new Date();
    }
};