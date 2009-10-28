Ext.ux.UserPanel = Ext.extend(Ext.Panel, {
    title: 'Information',
    frame: true,
    border: false,
    padding: 4,
    URLS: {
        get_user_courses: null,
        del_user_course: null,
        add_user_course: null,
        get_user_data: null
    },
    interval: 500,
    initComponent: function(){

        var config = {
            items: [
                this._createUserForm(),
                this._createUserCoursesPanel()
            ],
            tbar: [
                {text: 'Client', iconCls: 'icon-info', handler: function() {}},
                {text: 'Search', iconCls: 'icon-info', handler: function() {}},
                {text: 'Add new',iconCls: 'icon-plus', handler: function() {}}
            ]
        }
        Ext.apply(this, config);
        Ext.ux.UserPanel.superclass.initComponent.call(this);
    },
    afterRender: function(){
        Ext.ux.UserPanel.superclass.afterRender.call(this);
        this.loadUserData();
        this._initMonitoring();
    },
    _initMonitoring: function(){
        setInterval(this.loadUserData.createDelegate(this), this.interval*1000);
    },
    loadUserData: function(){
        Ext.Ajax.request({
            url: this.URLS.get_user_data,
            method: 'POST',
            success: function(response) {
                var json = Ext.util.JSON.decode(response.responseText);
                if (json.rfid_code == this.card) return;
                this.card = json.rfid_code;
                if (this.card != '00000000') {
                    this.client_form.getForm().setValues(json);
                    this.course_store.user_rfid_code = this.card;
                    this.course_store.setBaseParam('rfid_code', this.card);
                    this.course_store.load();
                }else{
                    this.client_form.getForm().reset();
                    this.course_store.user_rfid_code = null;
                    this.course_store.baseParams = {};
                    this.course_store.removeAll();
                }
            },
            scope: this
        });
    },
    _createCourseStore: function(){
        this.course_store = new Ext.data.JsonStore({
            storeId: 'UserCourses',
            //autoLoad: true,
            autoDestroy: true, // destroy store when the component the store is bound to is destroyed
            root: 'courses', // get data from this key
            idProperty: 'id',
            user_rfid_code: null,
            fields: [
                {name: 'id', type: 'int'},
                'title',
                {name: 'reg_date', type: 'date'},
                {name: 'exp_date', type: 'date'},
                {name: 'count', type: 'int'},
                {name: 'course_id', type: 'int'},
                {name: 'deleteable', type: 'boolean'},
                {name: 'is_old', type: 'boolean'}
            ],
            proxy: new Ext.data.HttpProxy({
                method: 'POST',
                url: this.URLS.get_user_courses
            })
        });
        return this.course_store;
    },
    _createUserCoursesPanel: function(){
        this.user_courses = new Ext.Panel({
            frame: false,
            border: false,
            height: 60,
            flex: 1,
            margins: '1 0 0 0',
            autoScroll: true,
            items: {
                xtype: 'ext:ux:user-courses',
                store: this._createCourseStore(),
                del_course_url: this.URLS.del_user_course,
                add_course_url: this.URLS.add_user_course
            }
        });
        return this.user_courses;
    },
    _createUserForm: function(){
        this.client_form = new Ext.form.FormPanel({
            standardSubmit: true,
            labelWidth: 100,
            frame: false,
            defaults: {
                style: {width: '100%'}
            },
            items:[
                new Ext.form.TextField({ name: 'first_name', fieldLabel: 'First name', allowBlank: false }),
                new Ext.form.TextField({ name: 'last_name', fieldLabel: 'Last name', allowBlank: false }),
                new Ext.form.TextField({ name: 'email', fieldLabel: 'E-mail', allowBlank: false })
            ],
            buttons: [
                { text: 'Surchange', handler: function() {} },
                { text: 'Assign', handler: function() {} },
                { text: 'Apply', handler: function() {} },
            ]
        });
        return this.client_form;
    }
});

Ext.reg('ext:ux:user-panel', Ext.ux.UserPanel);