$(document).ready(function(){
var form = $('.follow_form');
     $(document).on('click','.not_followed',function (e) {
        e.preventDefault();
        var data = {};
        data.user_to_follow = $(this).data('user_to_follow');
        var csrf_token = $('.follow_form [name="csrfmiddlewaretoken"]').val();
        data["csrfmiddlewaretoken"] = csrf_token;
        var url = '/user/follow/';

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
            $(this).removeClass('not_followed').addClass('followed');
            $(this).find('span').text('Unfollow');
            $('#user').find('span.followers_counter').text(json.number_followers);
            $('div.post_user').find('span.followers_counter').text(json.number_followers)
            }
        })
    });
     $(document).on('click','.followed',function (e) {
        e.preventDefault();
        var data = {};
        data.user_to_follow = $(this).data('user_to_follow');
        var csrf_token = $('.follow_form [name="csrfmiddlewaretoken"]').val();
        data["csrfmiddlewaretoken"] = csrf_token;
        var url = '/user/unfollow/';

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            cache: true,
            context: this,
            success: function(json){
                $(this).removeClass('followed').addClass('not_followed');
                $(this).find('span').text('Follow');
                $('#user').find('span.followers_counter').text(json.number_followers);
                $('div.post_user').find('span.followers_counter').text(json.number_followers);
            }
        })
    });
});
