Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    emptyText: 'No courses assigned yet',
    frame: true,
    border: false,
    loadingText: 'loading',
    tpl: new Ext.XTemplate(
        '<tpl for="rows">',
            '<dl <tpl if="is_old">class="old-user-course"</tpl>>',
                '<tpl for="parent.columns">',
                '<dt style="width:{width}%;text-align:{align};"><em unselectable="on">',
                    '{[values.tpl.apply(parent)]}',
                '</em></dt>',
                '</tpl>',
                '<div class="x-clear"></div>',
            '</dl>',
        '</tpl>'
    ),
    columns: [{
        header: 'Title',
        width: .41,
        dataIndex: 'title'
    },{
        header: 'Count',
        width: .1,
        align: 'right',
        dataIndex: 'count'
    },{
        header: 'Begins',
        width: .2,
        tpl: '{reg_date:date("M d")}',
        align: 'right',
        dataIndex: 'reg_date'
    },{
        header: 'Expires',
        width: .2,
        tpl: '{exp_date:date("M d")}',
        align: 'right',
        dataIndex: 'exp_date'
    },{
        width: 0.09,
        dataIndex: 'id',
        tpl: '<tpl if="deleteable"><div class="delete-user-course" course_id="{id}">&nbsp;</div></tpl>'
    }],
    initComponent: function(){
        Ext.ux.UserCourses.superclass.initComponent.call(this);
        this.add_window = new Ext.Window({
            title: 'Add course',
            closeAction: 'hide',
            draggable: false,
            modal: true,
            hidden: true,
            items: new Ext.form.FormPanel({
                frame: true,
                items: [{
                    xtype: 'numberfield',
                    fieldLabel: 'Count',
                    name: 'count',
                    minValue: 1,
                    maxValue: 999,
                    allowBlank: false,
                    allowNegative: false,
                    value: 8,
                    maxLength: 3
                }]
            }),
            buttons: [{
                text: 'Add',
                scope: this,
                handler: function(){
                    var form = this.add_window.get(0).getForm();
                    if (form.isValid()){
                        this.add_window.hide();
                        this.add_window.node.count = form.findField('count').getValue();
                        form.reset();
                        this.addCourse(this.add_window.node);
                    }
                }
            },{
                text: 'Cancel',
                handler: function(){
                    this.add_window.hide();
                    this.add_window.get(0).getForm().reset();
                },
                scope: this
            }]
        });
    },
    afterRender: function(){
        Ext.ux.UserCourses.superclass.afterRender.call(this);
        new Ext.dd.DropTarget(this.ownerCt.getEl(), {
            ddGroup:'t2schedule',
            notifyDrop:function(dd, e, node) {
                if (this.getStore().user_rfid_code){
                    this.add_window.node = node.node;
                    this.add_window.setTitle(node.node.text);
                    this.add_window.show();
                    return true;
                }else{
                    return false;
                }
            }.createDelegate(this)//notifyDrop
        });//Ext.dd.DropTarget
    },
    addCourse: function(course){
        Ext.Ajax.request({
            url: this.add_course_url,
            method: 'POST',
            params: {
                rfid_code: this.getStore().user_rfid_code,
                course: course.id,
                count: course.count
            },
            success: function(response){
                var result = Ext.util.JSON.decode(response.responseText);
                if (result.success){
                    var store = this.getStore();
                    var r = new store.recordType(result.data, result.data[store.idProperty]);
                    store.insert(0, r);
                    this.addDeleteButtonHandler();
                }else{
                    Ext.ux.msg(result.errors, '', Ext.Msg.WARNING);
                }
            },
            scope: this
        });
    },
    refresh: function(){
        Ext.ux.UserCourses.superclass.refresh.call(this);
        this.addDeleteButtonHandler();/*
        Ext.each(Ext.DomQuery.select('div.delete-user-course'), function(item){
             Ext.get(item).on('click', this.clickDelButton, this)
        }, this);*/
    },
    addDeleteButtonHandler: function(){
        Ext.each(Ext.DomQuery.select('div.delete-user-course'), function(item){
             Ext.get(item).on('click', this.clickDelButton, this)
        }, this);
    },
    clickDelButton: function(e, t, o){
        var store = this.getStore();
        var $record = store.getById(Ext.get(t).getAttribute('course_id'));
        Ext.MessageBox.confirm($record.get('title'), 'Are you sure you want to delete event?',(function(bt){
            if(bt=='yes'){
                Ext.Ajax.request({
                   url: this.del_course_url,
                   success: function(response){
                       var data = Ext.decode(response.responseText);
                       if (data.result){
                           store.remove($record);
                       }else{
                           Ext.ux.msg('Failure', data.msg, Ext.Msg.WARNING);
                       }
                   },
                   params: { id: $record.id }
                });
            }
        }).createDelegate(this));

    }
});

Ext.reg('ext:ux:user-courses', Ext.ux.UserCourses);