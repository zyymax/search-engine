$(function (){
    if($("#no_account") && $("#no_account").text() == '1'){
        alert('该微信公众账号还未收录，请先添加该微信公众账号。');
        window.location.href = '/submit/account';
    }
    $("#submit_button").click(function (){
        var postdata = '';
        var wxid     = $("#wxid").val();
        var aname    = $("#aname").val();
        var qrlink   = $("#qrlink").val();
        var desc     = $("#desc").val();
        var biz     = $("#biz").val();
        var score     = $("#score").val();
        var xsrf     = getCookie('_xsrf');
        var self_submit = document.getElementById("self_submit").checked ? 1 : 0;

        if(aname=='' || desc == '') {
            alert('该页面所有输入框都要填写');
            return false;
        }

        var fck = check_form(wxid, qrlink);
        if(!fck) {
            return false;
        }
        postdata = build_data(wxid, aname, qrlink, desc, self_submit, biz, score, xsrf);

        $.ajax({
            type: "POST",
            url: location.href,
            data: postdata,
            success: function(msg){
                if(msg == 'success') {
                    alert('感谢您的提交，我们会尽快审核。');
                    window.location.href = '/submit/account';
                } else {
                    alert('感谢您的提交，该账号已存在，点击确定进入该账号页面');
                    window.location.href = '/account/' + msg;
                }
            }
        });
    });

    var build_data = function (){
        var data = '';
        var fields = ['wxid', 'aname', 'qrlink', 'desc', 'self_submit', 'biz', 'score', '_xsrf'];
        for(var i=0,len=arguments.length;i<len;i++){
            if(typeof arguments[i] !="undefined"){
                data = data + fields[i] + "=" + arguments[i] ;
                if(i != len -1){
                    data = data + '&' ;
                }
            }
        }
        return data;
    };

    var check_form = function(wxid, qrlink){
        if(!isWxid(wxid)) {
            alert('公众账号微信id不符合规则');
            return false;
        }
        if(!checkWeiboImage(qrlink)) {
            alert('二维码图片地址不正确，请检查是否添加http://以及是否以.jpg/png等结尾，不能是photo.weibo.com的域名');
            return false;
        }
        return true;
    };

    $("#submit_essay_button").click(function (){
        var postdata = '';
        var wxid     = $("#wxid").val();
        var link     = $("#link").val();
        var title    = $("#title").val();
        var time     = $("#time").val();
        var digest   = $("#digest").val();
        var source   = $("#source").val() == '' ? link : $("#source").val();
        var xsrf     = getCookie('_xsrf');

        if(title== '' || time == '' || source == '' || digest == '') {
            alert('该页面除原文链接之外所有输入框都要填写');
            return false;
        }

        var fck = check_form_essay(wxid, link);
        if(!fck) {
            return false;
        }
        link = encodeURIComponent(link);
        source = encodeURIComponent(source);
        postdata = build_data_essay(wxid, link, title, time, digest, source, xsrf);

        $.ajax({
            type: "POST",
            url: "/submit/essay",
            data: postdata,
            success: function(msg){
                if(msg == 'success') {
                    alert('感谢您的提交，我们会尽快审核。');
                    history.back();
                } else if(msg == 'accountnotexist'){
                    alert('该公众账号还未收录，您可以先提交该公众账号再提交该文章。');
                    window.location.href = '/submit/account';
                }  else if(msg == 'verifying'){
                    alert('该公众账号还在审核中，请耐心等候。或者到我的微博http://weibo.com/alexzhan 告诉我。');
                    window.location.href = '/submit/account';
                }  else if(msg.indexOf('essay:') === 0){
                    alert('该文章已存在，感谢您的提交。');
                    history.back();
                }
            }
        });
    });

    var check_form_essay = function(wxid, link){
        if(!isWxid(wxid)) {
            alert('公众账号微信id不符合规则');
            return false;
        }
        if(!checkEssayLink(link)) {
            alert('文章地址不正确，请检查是否添加http://和是否是mp.weixin.qq.com上的文章');
            return false;
        }
        return true;
    };

    var build_data_essay = function (){
        var data = '';
        var fields = ['wxid', 'link', 'title', 'time', 'digest', 'source', '_xsrf'];
        for(var i=0,len=arguments.length;i<len;i++){
            if(typeof arguments[i] !="undefined"){
                data = data + fields[i] + "=" + arguments[i] ;
                if(i != len -1){
                    data = data + '&' ;
                }
            }
        }
        return data;
    };
});
