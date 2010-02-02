jQuery(document).ready(function(){
    (function(){
        var div = $('#mounth_picker');
        var inputs = {
            year: div.prev().prev(),
            month: div.prev(),
            form: $('#mounth-form')
        };
        $('#mounth_picker').monthpicker({
            elements: [
                    {tpl:"year",opt:{
                            range: [div.html(), (new Date()).getFullYear()],
                            value: inputs.year.val()
                    }},
                    {tpl:"month",opt:{
                            value: inputs.month.val()
                    }}
            ],
            onChanged: function(date, el){
                inputs.year.val(date.year);
                inputs.month.val(date.month);
                inputs.form.submit();
                //$(el).prev().val(date.month).prev().val(date.year);
            }
        })
    })();
});
