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
                data.msg && Ext.ux.msg(data.msg, '', Ext.MessageBox.WARNING);
                data.result && callback() || revert_callback();
            }
        });
    },
    draggable: function(calEvent, $calEvent){
        return calEvent.start > new Date();
    }
};