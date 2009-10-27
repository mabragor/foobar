Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    emptyText: 'No courses assigned yet',
    frame: true,
    border: false,
    loadingText: 'loading',
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
    afterRender: function(){
        Ext.ux.UserCourses.superclass.afterRender.call(this);
        new Ext.dd.DropTarget(this.ownerCt.getEl(), {
            ddGroup:'t2schedule',
            notifyDrop:function(dd, e, node) {
                this.addCourse(node.node);
                /*
                var store = this.getStore();
                var r = new store.recordType({title: node.node.text, count: 8, course_id: node.node.id, deleteable: true});
                store.insert(0, r);
                this.addDeleteButtonHandler();*/
                return true;
            }.createDelegate(this)//notifyDrop
        });//Ext.dd.DropTarget
    },
    addCourse: function(course){
        Ext.Ajax.request({
            url: this.add_course_url,
            method: 'POST',
            params: {
                rfid_code: this.getStore().user_rfid_code,
                course: course.id
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