$(document).ready(function(){
var form = $('.like_form');
     $(document).on('click','.not_liked',function (e) {
        e.preventDefault();
        var data = {};
        data.post_id = $(this).data('post_id');
        var csrf_token = $('.like_form [name="csrfmiddlewaretoken"]').val();
        data["csrfmiddlewaretoken"] = csrf_token;
        var url = form.attr("action");

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            cache: true,
            context: this,
            statusCode: {
                500: function() {
                    window.location.href = '/login/';
                    }
                },
            success: function(json){
            $(this).removeClass('not_liked').addClass('liked');
            $(this).find('span').text(json.number_likes);
            }
        })
    });
     $(document).on('click','.liked',function (e) {
        e.preventDefault();
        var data = {};
        data.post_id = $(this).data('post_id');
        var csrf_token = $('.like_form [name="csrfmiddlewaretoken"]').val();
        data["csrfmiddlewaretoken"] = csrf_token;
        var url = form.attr("action");

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            cache: true,
            context: this,
            success: function(json){
                $(this).removeClass('liked').addClass('not_liked');
                $(this).find('span').text(json.number_likes);
            }
        })
    });
});
